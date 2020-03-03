#!/bin/env python

import math
import time
from abc import ABC

import geojson
import requests
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
    def __init__(self, auth_token, api_base_url="https://mvillage.um.city/api"):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.session.headers = {'X-API-KEY': auth_token}

    def post_json_message(self, endpoint, json_message):
        return self.session.post("%s%s" % (self.api_base_url, endpoint), json=json_message)


class MovingPoint(geojson.Point):
    """
    Defines a GeoJson point that is moving. Speed in m/s, heading in degrees
    """
    def __init__(self, speed=0, heading=0, **extra):
        self.speed = speed
        self.heading = heading
        super().__init__(**extra)


class V2XMessageType(ABC):
    """
    Types of V2X messaging to support, per SAE J2735
    """
    frequency_hz = 1

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


class BSM(V2XMessageType):
    """
    Basic Safety Message
    """
    frequency_hz = 10
    temp_id = 0

    # TODO: allow initialization of these
    _base_params = {
        "id": "PathFollower 0.1",
        "idFixed": "1212",
        "messageSet": "J2735_200612",
        "vehicleLength": 4.5,
        "vehicleWidth": 1.83,
    }

    def endpoint(self, rsu_id):
        # Assumes OCTANE of course!
        return "/v2x/rsu/%s/bsm" % rsu_id

    def as_message(self, moving_point):
        self.temp_id += 1

        message = {
            "idTemporary": self.temp_id,
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

    def __init__(self, geojson_filename, velocity_ms):
        """

        :param geojson_file: A geojson file that contains a Feature with a LineString
        :param velocity_ms: Object velocity in meters/sec
        """
        with open(geojson_filename) as geojson_file:
            geo_feature = geojson.load(geojson_file)

        self.geojson_path = geojson.utils.coords(geo_feature)
        self.velocity_ms = float(velocity_ms)

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
                point_count = math.ceil((distance_m / self.velocity_ms) * self.frequency_hz)

                for (point_lng, point_lat) in self.geod.npts(prev_path_lng, prev_path_lat, path_lng, path_lat,
                                                             point_count):
                    if prev_point_lat and prev_point_lng:
                        heading, _, _ = self.geod.inv(prev_point_lng, prev_point_lat, point_lng, point_lat)

                        yield MovingPoint(speed=self.velocity_ms, heading=heading, coordinates=(point_lng, point_lat))

                    prev_point_lat = point_lat
                    prev_point_lng = point_lng

            prev_path_lat = path_lat
            prev_path_lng = path_lng

    def follow(self, octane_instance, rsu_id):
        """
        Given the path this object represents, follow it, posting v2x messages to an OCTANE instance
        at the proper frequency
        """
        start = time.time()
        for moving_point in self.path():
            # post the v2x message, then sleep until it's time to post another
            response = octane_instance.post_json_message(self.endpoint(rsu_id), self.as_message(moving_point))
            response.raise_for_status()

            # Sleep for the remaining time. Right now if that's negative just continue
            elapsed = time.time() - start
            remaining = self.time_per_msg_s - elapsed
            if remaining > 0:
                time.sleep(remaining)
            start = time.time()


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
    octane = OctaneInstance("reticulatingsplines")
    vpf = VehiclePathFollower("roundabout.json", 4.5)
    vpf.follow(octane, 1)


if __name__ == '__main__':
    main()