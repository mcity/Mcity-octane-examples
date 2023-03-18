"""
mapp-single-waypoint-nav.py

Sample Mcity OS script to control a MAPP, moving to a specific (lat, long) at a specified speed.

Pass in the values as command line arguments or edit them below.
"""
import os
import sys
import time
import socketio
from mapp_common import MAPP_Client
import signal

if len(sys.argv) == 4:
    lat = float(sys.argv[1])
    long = float(sys.argv[2])
    meters_per_second = float(sys.argv[3])
else:
    exit()

# Load environment variables and configure
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.mvillage.um.city/')
proxy_id = os.environ.get('MCITY_ROBOT_ID', 1)

# If no API Key provided, exit.
if not api_key:
    print("NO API KEY SPECIFIED. SET MCITY_OCTANE_KEY. EXITING")
    exit()

def signal_handler(sig, frame):
    mapp_client.disable(proxy_id)
    exit()


if __name__ == '__main__':

    # Make connection.
    mapp_client = MAPP_Client(api_key, server)
    sio = socketio.Client()
    sio.register_namespace(namespace_handler=mapp_client)
    sio.connect(server)

    # Wait until we are subscribed to the ipc channel for publishing
    while not mapp_client.connected:
        time.sleep(0.02)

    mapp_client.enable(proxy_id)

    signal.signal(signal.SIGINT, signal_handler)

    while not mapp_client.enable_sent:
        time.sleep(0.02)

    # Send request. Ideally this is incorporated into a running interpreter, so the connection above is already
    # available before calling this function, for lowest latency
    mapp_client.single_waypoint_nav(proxy_id, lat, long, meters_per_second)

    # Wait until the message has been sent
    while not mapp_client.single_waypoint_nav_sent:
        time.sleep(0.02)

    sio.wait()

    sio.disconnect()
