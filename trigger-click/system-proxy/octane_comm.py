import asyncio
import os

import socketio
import logging
import sys

from dotenv import load_dotenv

from utils import RTKUtility

logfile = '/home/mcity/logs/octane_comm.log'
logging.basicConfig(filename=logfile, level=logging.INFO,
                    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    )
sio = socketio.AsyncClient(logger=logging)
logging.info('Created socketio client')

load_dotenv()
OCTANE_URL = os.environ['OCTANE_URL']
OCTANE_KEY = os.environ['OCTANE_KEY']


class OctaneComm(socketio.AsyncClientNamespace):
    async def on_connect(self):
        print('Connected to server [{}], emitting auth'.format(OCTANE_URL))
        await self.emit('auth', {'x-api-key': OCTANE_KEY},
                        namespace='/octane')

    def on_auth_ok(self, data):
        logging.info('Auth OK')

    def on_disconnect(self):
        logging.info('Disconnected')

    async def connect(self):
        print( 'Attempting to connect to {}'.format(OCTANE_URL))
        await sio.connect(OCTANE_URL, namespaces=['/octane'])

    async def send_beacon_update(self):
        logging.debug('Emitting beacon update')
        latitude, longitude, heading, speed = RTKUtility.get_gps_latlong()
        if latitude is None:
              return
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
    # Send beacon updates 3 times per second
    frequency = 1 / 3

    comm = OctaneComm('/octane')
    sio.register_namespace(comm)
    await comm.connect()
    while True:
        await comm.send_beacon_update()
        await asyncio.sleep(frequency)


loop = asyncio.get_event_loop()
loop.run_until_complete(octane_updater())

