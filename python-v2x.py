"""
python-v2x.py
Sample Mcity OCTANE Python script for interacting with V2X AACE data.
"""
import os
import json
from dotenv import load_dotenv
import socketio
import requests

#Load environment variables
load_dotenv()
api_key = os.environ.get('MCITY_OCTANE_KEY', None) 
server = os.environ.get('MCITY_OCTANE_SERVER', 'http://localhost:5000')
namespace = "/octane"

#If no API Key provided, exit.
if not api_key:
    print ("No API KEY SPECIFIED. EXITING")
    exit()

#Query all intersections to get a listing of possible intersections for use.
#First build a re-usable header for queries.
headers = {
    'accept': 'application/json',
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
}

#Make the get query
uri = server + '/api/intersections'
response = requests.get(uri, headers=headers)
json_data = json.loads(response.text)

#Plymouth/Nixon is ID 157/
#We found this by browsing the above list.
#You can print the list with: print(json_data)
for item in json_data['intersections']:
    if item['id'] == 157:
        #For any given intersection that is V2X enabled
        #A V2X intersection id is assigned. This identifier will be present
        #on all messages from this infrastructure
        #This ID can also be used to subscribe to a stream with only messages
        #from this device.
        v2xid = item['v2xIntersectionId']

#This is the intersection we'd like to listen to events from.

print (v2xid)

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
    #After the first channel list you have logged in.
    #For this example we'll use this to signify the start of our session.
    #At this point let's join the stream for the RSU we are interested in.
    #The channel format is v2x_rsu_[id]_parsed (or raw)
    channel = 'v2x_rsu_' + v2xid + '_parsed'
    #Show all the rsu messages parsed:
    #channel = 'v2x_rsu_parsed'
    #Show all the obu messages raw:
    #channel = 'v2x_obu_raw'
    # let's join the V2X channel.
    sio.emit('join', {'channel': channel}, namespace=namespace)

@sio.on('v2x_SPaT', namespace=namespace)
def on_spat(data):
    """
    Event fired for each V2X Parsed SPaT message
    """
    print(data)

@sio.on('v2x_raw', namespace=namespace)
def on_raw(data):
    """
    Event fired for each V2X RAW message
    """
    print(data)

@sio.on('disconnect', namespace=namespace)
def on_disconnect():
    """
    Event fired on disconnect.
    """
    print('disconnected from server')

#Make connection.
sio.connect(server, namespaces=[namespace])
sio.wait()