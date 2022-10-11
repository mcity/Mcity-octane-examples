#! /usr/bin/env python3
# listen-intersections.py

import os
import socketio
import time

# mvillage environment
server = "wss://octane.mvillage.um.city"
api_key = "reticulatingsplines"

# mcity environment
#server = "wss://octane.um.city"
#api_key = "my_octane_token"

namespace = "/octane"

sio = socketio.Client()

def send_auth():
    """
    Emit an authentication event.
    """
    sio.emit('auth', {'x-api-key': api_key}, namespace=namespace)

@sio.on('connect', namespace=namespace)
def on_connect():
    """
    Handle connection event and send authentication key
    """
    send_auth()

@sio.on('auth_ok', namespace=namespace)
def on_auth_ok(data):
    global sio
    print('\n\ngot auth ok event')
    print('Subscribing to v2x_rsu_parsed channel')
    sio.emit('join', {'channel': 'v2x_rsu_parsed'}, namespace=namespace)

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

@sio.on('v2x_SPaT', namespace=namespace)
def on_v2x_spat(data):
    if(data['id'] == 'beef'): # example Mcity id: 0a0c
        #print(data)
        print("\n")
        print_spat(data)


def on_message(client, userdata, msg):
    global api_key
    if msg.topic == 'ESS/McityApiKey':
        api_key = msg.payload.decode('utf-8')
        print('Received API Key {}'.format(api_key))


# prints spat in viewable format
def print_spat(data):
    red = data['red'][8:16]
    yellow = data['yellow'][8:16]
    green = data['green'][8:16]
    space = " "
    print(data['updated'])
    print("Ph:  1 2 3 4 5 6 7 8")
    print("RED  " + space.join(red))
    print("YEL  " + space.join(yellow))
    print("GRE  " + space.join(green))


if not api_key:
    print("Waiting for API key")
    while not api_key:
        time.sleep(1)
    print("API key loaded, connecting")

sio.connect(server, namespaces=[namespace])
sio.wait()
