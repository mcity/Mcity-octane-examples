"""
mapp-listener.py

Sample Mcity OS script that listens to everything published on the robot_proxy channel.
"""
import os
import time
import socketio
from mapp_common import MAPP_Client


# Load environment variables and configure
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.mvillage.um.city/')

# If no API Key provided, exit.
if not api_key:
    print("NO API KEY SPECIFIED. EXITING")
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

    sio.wait()

    sio.disconnect()