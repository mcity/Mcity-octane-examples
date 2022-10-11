"""
octane_comm.py

Script to connect Mcity RTK and Oxford RTK devices to Mcity OS as beacons. Requires an Mcity OS Beacon or Oxford NCOM
listener to be running, populating a local redis instance with position data.
"""
import asyncio
import logging
import os

import socketio
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


class OctaneComm(socketio.AsyncClientNamespace):
    async def on_connect(self):
        print(f'Connected to server [{server}]')
        await self.emit('auth', {'x-api-key': api_key}, namespace='/octane')

    async def connect(self):
        print('Attempting to connect to {}'.format(server))
        await sio.connect(server, namespaces=['/octane'])

    async def send_beacon_update(self):
        latitude, longitude, heading, speed = RTKUtility.get_gps_latlong()
        if latitude is None:
            return

        logging.info(f'Emitting beacon update lat = {latitude}, long = {longitude}')

        message = {
            "id":  RTKUtility.get_device_id_clean(),
            "payload": {
                "state": {
                    "dynamics": {
                        "longitude": float(longitude),
                        "latitude": float(latitude),
                        "heading": 0,
                        "velocity": 0,
                        "acceleration": 0,
                        "elevation": 0,
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
    print("Waiting for beacon data")
    while True:
        await comm.send_beacon_update()
        await asyncio.sleep(frequency)


loop = asyncio.get_event_loop()
loop.run_until_complete(octane_updater())
