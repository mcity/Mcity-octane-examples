"""
python-socketio.py
Sample Mcity OCTANE python socketio script
"""
import os
import time
from dotenv import load_dotenv
import socketio

#Load environment variables
load_dotenv()
api_key = os.environ.get('MCITY_OCTANE_KEY', 'armadillo') 
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.um.city/')
namespace = "/octane"

#If no API Key provided, exit.
if not api_key:
    print ("No API KEY SPECIFIED. EXITING")
    exit()

#Create an SocketIO Python client.
sio = socketio.Client()
# Async client is available also: sio = socketio.AsyncClient()

def send_auth():
    """
    Emit an authentication event.
    """
    sio.emit('auth', {'x-api-key': api_key}, namespace=namespace)

#Define event callbacks
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
    print('Join received with ', data)
    
@sio.on('channels', namespace=namespace)
def on_channels(data):
    """
    Event fired when a user requests current channel information.
    """
    print('Channel information', data)

@sio.on('disconnect', namespace=namespace)
def on_disconnect():
    """
    Event fired on disconnect.
    """
    print('disconnected from server')

@sio.on('auth_ok', namespace=namespace)
def on_auth_ok(data):
    global sio
    print('\n\ngot auth ok event')
    print('Subscribing to ipc channel')
    sio.emit('join', {'channel': 'ipc'}, namespace=namespace)

#Make connection.
sio.connect(server, namespaces=[namespace])

time.sleep(2)
print('Sending trigger for ID 1')
sio.emit('ipc_message', {"type": "TRIGGER", "payload": {"id": 1, "triggerType": "software", "state": {"activated": True}}}, namespace=namespace)
sio.disconnect


