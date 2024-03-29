
"""
mapp-move-and-reverse.py

Sample Mcity OS script to control a MAPP, moving first forward and then in reverse.

Either edit the default values below or pass in the values as command line arguments.
"""
import os
import sys
import time
import socketio
from mapp_common import MAPP_Client
import signal

if len(sys.argv) == 4:
    meters = float(sys.argv[1])
    meters_per_second = float(sys.argv[2])
    wait_time = float(sys.argv[3])
else:
    meters = 1.0
    meters_per_second = 0.5
    wait_time = 1.0

# Load environment variables
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.mvillage.um.city/')
proxy_id = os.environ.get('MCITY_ROBOT_ID', 1)

# If no API Key provided, exit.
if not api_key:
    print("NO API KEY SPECIFIED. SET MCITY_OCTANE_KEY. EXITING")
    exit()

def on_robot_proxy(data):
    """
    Override the on_robot_proxy event handler to wait for the goal result so we know when to reverse.
    """
    global reverse
    if str(data.get('type', None)) == 'goal_result':
        reverse = True
    print(data)

def signal_handler(sig, frame):
    mapp_client.disable(proxy_id)
    sys.exit(0)

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
    mapp_client.move_distance(proxy_id, meters, meters_per_second)

    while not mapp_client.goal_completed:
        print("Waiting for goal_completed")
        print(mapp_client.goal_completed)
        time.sleep(0.02)

    time.sleep(wait_time)

    mapp_client.move_distance(proxy_id, -1.0 * meters, meters_per_second)

    sio.wait()

    sio.disconnect()