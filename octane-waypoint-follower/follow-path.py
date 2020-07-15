#!/bin/env python

import math
import time
from abc import ABC

import geojson
import requests
import socketio
from pyproj import Geod

"""
Given a path in GeoJSON, this set of classes will work out a linear traversal of them based on a model (vehicle, 
person, etc.) It will produce a set of V2X messages and insert them into OCTANE, attempting to produce them 
according to the expected timing for the particular message type (BSM, PSM, etc.)
 
The general flow is
    import geojson file - here we're expecting a LineString or MultiPoint
    initialize type of message (which dictates frequency) - see VehiclePathFollower and HumanPathFollower
    figure out distance interpolation between each segment - accounts for randomly drawn lines
    produce V2X messages with the proper distance separation and frequency
    insert them into OCTANE
"""


class OctaneInstance:
    """
    Represents an OCTANE connection

    TODO: this should go away in lieu of a more full-featured API implementation
    """
    def __init__(self, auth_token, api_server="https://octane.mvillage.um.city"):
        self.auth_token = auth_token
        self.api_server = api_server

        self.api_base_url = f"{api_server}/api"
        self.session = requests.Session()
        self.session.headers = {'X-API-KEY': auth_token}
        self.socket = socketio.Client()
        self.socket.register_namespace(self.OctaneNamespace(self))

    def __enter__(self):
        # Connect to websocket
        self.socket.connect(self.api_server, transports=None, namespaces=[self.OctaneNamespace.namespace])

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.disconnect()

    def emit(self, channel, payload):
        self.socket.emit(channel, payload, namespace=self.OctaneNamespace.namespace)

    def post_json_message(self, endpoint, json_message):
        return self.session.post("%s%s" % (self.api_base_url, endpoint), json=json_message)

    def get(self, endpoint):
        return self.session.get("%s%s" % (self.api_base_url, endpoint))

    class OctaneNamespace(socketio.ClientNamespace):
        namespace = "/octane"

        def __init__(self, octane_instance):
            self.octane_instance = octane_instance
            super().__init__(self.namespace)

        def on_connect(self):
            self.octane_instance.socket.emit('auth', {'x-api-key': self.octane_instance.auth_token}, 
                                             namespace=self.namespace)

        def on_disconnect(self):
            self.octane_instance.socket.disconnect()


class MovingPoint(geojson.Point):
    """
    Defines a GeoJson point that is moving. Speed in m/s, heading in degrees
    """
    def __init__(self, speed=0, heading=0, **extra):
        self.speed = speed
        self.heading = heading
        super().__init__(**extra)

    def __str__(self):
        return f"MovingPoint: lat {self.coordinates[1]:>-3.9f}, lon {self.coordinates[0]:>-3.9f}, {self.speed:>3.1f}m/s, heading {self.heading:03.2f}" 


class V2XMessageType(ABC):
    """
    Types of V2X messaging to support, per SAE J2735
    """
    frequency_hz = 1
    protocol = "J2735_201603"

    @property
    def time_per_msg_s(self):
        """
        How often to send a message, in seconds. Fractions of a second are fine.
        """
        return 1.0/self.frequency_hz

    def endpoint(self, rsu_id):
        pass

    def as_message(self, moving_point):
        """
        Given a MovingPoint, return a dict that can be POSTed to OCTANE as JSON
        :param moving_point: An instance of MovingPoint
        :return: a dict of message params
        """
        pass

    @property
    def name(self):
        """
        Message type that this class supports. Corresponds to Octane's "messageType" field
        """
        pass


class BSM(V2XMessageType):
    """
    Basic Safety Message
    """
    frequency_hz = 10
    id = "000003B5" # 949 for now, in the Mcity range. TODO: allow setting this

    # TODO: allow initialization of these
    _base_params = {
        "id": id,
        "idTemporary": id,
        "idFixed": id,
        "angle": 0.0, # TODO: compute!
        "messageSet": V2XMessageType.protocol,
        "vehicleLength": 4.5,
        "vehicleWidth": 1.83,
    }

    def endpoint(self, rsu_id):
        # Assumes OCTANE of course!
        return "/v2x/rsu/%s/bsm" % rsu_id

    @property
    def name(self):
        return "BSM"

    def as_message(self, moving_point):
        message = {
            "longitude": moving_point.coordinates[0],
            "latitude": moving_point.coordinates[1],
            "elevation": moving_point.coordinates[2] if len(moving_point.coordinates) > 2 else 0,
            "speed": moving_point.speed,
            "heading": moving_point.heading
        }
        message.update(self._base_params)

        return message


class PSM(V2XMessageType):
    """
    Pedestrian Safety Message
    """
    frequency_hz = 5

    def endpoint(self, rsu_id):
        # Assumes OCTANE of course!
        return "/v2x/rsu/%s/psm" % rsu_id

    @property
    def name(self):
        return "PSM"

    def as_message(self, moving_point):
        raise NotImplementedError


class PathFollower(ABC):
    """
    Implements (V2X) path following for a given path and type of thing.

    Subclasses should implement the follow method, which will yield a
    location, speed, and heading. Frequency of sending is assumed to
    be constant, and defined by the class.
    """
    geod = Geod(ellps="WGS84")

    def __init__(self, geojson_filename, velocity_meters_per_s):
        """

        :param geojson_file: A geojson file that contains a Feature with a LineString
        :param velocity_meters_per_s: Object velocity in meters/sec
        """
        with open(geojson_filename) as geojson_file:
            geo_feature = geojson.load(geojson_file)

        self.geojson_path = geojson.utils.coords(geo_feature)
        self.velocity_meters_per_s = float(velocity_meters_per_s)

    def find_rsu(self, octane_instance):
        """
        Given the type of messages we want to send, find a compatible RSU. Currently just
        returns the first match. Could be extended to find nearest, etc.
        """
        response = octane_instance.get("/v2x/rsus")
        response.raise_for_status()

        for rsu in response.json().get("rsus", []):
            for radio in rsu.get("radiosSupported"):
                if radio["messageSet"] == self.protocol and radio["messageType"] == self.name \
                      and radio["txEnabled"]:
                    return rsu["id"]

        raise RuntimeError(f"Unable to find a suitable RSU to send {self.name()}s via {self.protocol}")

    def path(self):
        """
        Generates a path, which yields a point per frequency interval
        :return: Yields a point stream as a (latitude, longitude) tuple of floats
        """
        prev_path_lat = prev_path_lng = prev_point_lat = prev_point_lng = None
        for (path_lng, path_lat) in self.geojson_path:
            if prev_path_lat and prev_path_lng:
                # Compute the number of broadcasted points we'll need to satisfy
                # the frequency requirements, given the object's velocity between
                # the two waypoints. We'll always round up the number of broadcast
                # points, which for now will underreport velocity slightly.
                #
                distance_m = self.geod.line_length((prev_path_lng, path_lng), (prev_path_lat, path_lat))
                point_count = math.ceil((distance_m / self.velocity_meters_per_s) * self.frequency_hz)

                for (point_lng, point_lat) in self.geod.npts(prev_path_lng, prev_path_lat, path_lng, path_lat,
                                                             point_count):
                    if prev_point_lat and prev_point_lng:
                        heading, _, _ = self.geod.inv(prev_point_lng, prev_point_lat, point_lng, point_lat)
                        if (heading < 0):
                            heading += 360

                        yield MovingPoint(speed=self.velocity_meters_per_s, heading=heading, coordinates=(point_lng, point_lat))

                    prev_point_lat = point_lat
                    prev_point_lng = point_lng

            prev_path_lat = path_lat
            prev_path_lng = path_lng

    def follow(self, octane_instance, rsu_id=None):
        """
        Given the path this object represents, follow it, posting v2x messages to an OCTANE instance
        at the proper frequency
        """
        if not rsu_id:
            rsu_id = self.find_rsu(octane_instance)

        print(f"Traversing a path, sending {self.name}s via {self.protocol} to RSU {rsu_id}")

        start = time.time()
        for moving_point in self.path():
            # post the v2x message, then sleep until it's time to post another
            data = self.as_message(moving_point)
            print(moving_point, end="\r")

            octane_instance.emit(f"v2x_{self.name}", {'id': rsu_id, 'payload': data})

            # Sleep for the remaining time. Right now if that's negative just continue
            elapsed = time.time() - start
            remaining = self.time_per_msg_s - elapsed
            if remaining > 0:
                time.sleep(remaining)
            start = time.time()

        print("\n")


class VehiclePathFollower(PathFollower, BSM):
    """
    Implements path following for a vehicle.
    """
    pass


class HumanPathFollower(PathFollower, PSM):
    """
    Implements path following for a person.
    """
    pass


def main():
    with OctaneInstance("reticulatingsplines", "https://octane.mvillage.um.city") as octane:
        vpf = VehiclePathFollower("roundabout.json", 11)
        vpf.follow(octane)


if __name__ == '__main__':
    main()

