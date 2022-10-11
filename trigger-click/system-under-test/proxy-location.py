"""
python-beason-socketio.py
Sample Mcity OCTANE python socketio script to listen to beacon updates.
"""
import os
from dotenv import load_dotenv
import socketio

# Load environment variables
load_dotenv()
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.um.city/')
namespace = "/octane"

# If no API Key provided, exit.
if not api_key:
    print ("No API KEY SPECIFIED. EXITING")
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
    print('Subscribing to beacon channel')
    sio.emit('join', {'channel': 'beacon'}, namespace=namespace)
    sio.emit('join', {'channel': 'v2x_obu_parsed'}, namespace=namespace)

@sio.on('beacon_update', namespace=namespace)
def on_beacon_update(data):
    '''
    Fired each time a beacon sends us position data
    '''    
    print('Beacon update: ', data)

@sio.on('v2x_BSM', namespace=namespace)
def on_v2x(data):
    '''
    Fired each time a beacon sends us position data
    '''    
    print('Beacon update: ', data)


# Make connection, everything else is event based.
sio.connect(server, namespaces=[namespace])
sio.wait()

