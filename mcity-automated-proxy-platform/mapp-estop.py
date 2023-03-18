"""
mapp-estop.py

Sample Mcity OS script to estop a MAPP.

"""
import os
import socketio
import time
from mapp_common import MAPP_Client, mapp_sio

# Load environment variables and configure
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.mvillage.um.city/')
proxy_id = os.environ.get('MCITY_ROBOT_ID', 1)

# If no API Key provided, exit.
if not api_key:
    print("NO API KEY SPECIFIED. SET MCITY_OCTANE_KEY. EXITING")
    exit()


if __name__ == '__main__':
    # Make connection.
    mapp_client = MAPP_Client(api_key, server)
    sio = socketio.Client()
    sio.register_namespace(namespace_handler=mapp_client)
    sio.connect(server)

    # Wait until we are subscribed to the robot_proxy channel for publishing
    while not mapp_client.connected:
        time.sleep(0.02)

    # Send request. Ideally this is incorporated into a running interpreter, so the connection above is already
    # available before calling this function, for lowest latency
    mapp_client.estop(proxy_id)

    # Wait until the message has been sent
    while not mapp_client.estop_sent:
        time.sleep(0.02)

    sio.wait()

    sio.disconnect()
