"""
trigger-proxy.py

Sample Mcity OS script to request a proxy begin its scenario.
"""
import os
import time
from dotenv import load_dotenv
import socketio

# Load environment variables
load_dotenv()
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.mvillage.um.city/')
namespace = "/octane"
trigger_ready = False
trigger_sent = False

# If no API Key provided, exit.
if not api_key:
    print("No API KEY SPECIFIED. EXITING")
    exit()

# Create an SocketIO Python client.
sio = socketio.Client()
# Async client is available also: sio = socketio.AsyncClient()


def send_auth():
    """
    Emit an authentication event.
    """
    sio.emit('auth', {'x-api-key': api_key}, namespace=namespace)


# Define event callbacks
@sio.on('connect', namespace=namespace)
def on_connect():
    """
    Handle connection event and send authentication key
    """
    send_auth()


@sio.on('join', namespace=namespace)
def on_join(data):
    """
    Event fired when user joins a channel
    """
    global trigger_ready
    #print('Join received with ', data)
    if data.get('join', None) == 'ipc':
        trigger_ready = True


@sio.on('auth_ok', namespace=namespace)
def on_auth_ok(data):
    #print('\n\nGot auth ok event')
    print('Subscribing to ipc channel')
    sio.emit('join', {'channel': 'ipc'}, namespace=namespace)


def sent():
    global trigger_sent
    trigger_sent = True


def trigger(ipc_id):
    print(f"Sending trigger for ID {ipc_id} to {server}")
    sio.emit('ipc_message',
             {"type": "TRIGGER", "payload": {"id": ipc_id, "triggerType": "software", "state": {"activated": True}}},
             namespace=namespace, callback=sent)


if __name__ == '__main__':
    # Make connection.
    sio.connect(server, namespaces=[namespace])

    # Wait until we are subscribed to the ipc channel for publishing
    while not trigger_ready:
        time.sleep(0.02)

    # Send trigger request. Ideally this is incorporated into a running interpreter, so the connection above is already
    # available before calling this function, for lowest latency
    trigger(1)

    # Wait until the message has been sent
    while not trigger_sent:
        time.sleep(0.02)

    sio.disconnect()
