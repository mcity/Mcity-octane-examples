"""
public_proxy_location.py

Script to connect Mcity RTK and Oxford RTK devices to Mcity OS as beacons. Requires an Mcity OS Beacon or Oxford NCOM
listener to be running, populating a local redis instance with position data.
"""
import asyncio
import logging
import os

import socketio
from datetime import datetime, timezone
from dotenv import load_dotenv

from utils import RTKUtility

# logfile = 'logs/octane_comm.log'
# logging.basicConfig(filename=logfile, level=logging.INFO,
#                     format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
#                     )
sio = socketio.AsyncClient(logger=logging)
logging.info('Created socketio client')

load_dotenv()
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.mvillage.um.city/')

try:
    beacon_id = os.environ.get('MCITY_BEACON_ID', None)
    if not beacon_id:
        beacon_id = RTKUtility.get_device_id_clean()
except ValueError:
    logging.error("Unable to determine beacon ID. Either set MCITY_BEACON_ID or ensure wlan0 is configured.")
    exit(1)


class OctaneComm(socketio.AsyncClientNamespace):
    async def on_connect(self):
        #print(f'Connected to server [{server}]')
        await self.emit('auth', {'x-api-key': api_key}, namespace='/octane')

    async def connect(self):
        print('Connecting to {}'.format(server))
        await sio.connect(server, namespaces=['/octane'])

    async def send_beacon_update(self):
        latitude, longitude, heading, speed, reading_taken_s = RTKUtility.get_gps_latlong()
        if latitude is None or latitude == 0:
            return

	reading_taken_dt = datetime.fromtimestamp(reading_taken_s, timezone.utc)

        logging.info(f'Emitting beacon update lat = {latitude}, long = {longitude}')

        message = {
            "id":  beacon_id,
            "payload": {
                "state": {
                    "dynamics": {
                        "longitude": float(longitude),
                        "latitude": float(latitude),
                        "heading": heading,
                        "velocity": speed,
                        "acceleration": 0,
                        "elevation": 0,
			# Format is 2022-10-20T13:09:21.422Z
			"updated": reading_taken_dt.isoformat(sep='T', timespec='milliseconds')
                    }
                }
            }
        }
        await self.emit('beacon_message', message, namespace='/octane')


async def octane_updater():
    # Send beacon updates 5 times per second
    frequency = 1 / 5

    comm = OctaneComm('/octane')
    sio.register_namespace(comm)
    await comm.connect()
    print(f"Waiting for internal (redis) beacon data for beacon ID {beacon_id}")
    while True:
        await comm.send_beacon_update()
        await asyncio.sleep(frequency)


loop = asyncio.get_event_loop()
loop.run_until_complete(octane_updater())
