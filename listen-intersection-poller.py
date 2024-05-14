
import socketio
import time

# mcity environment
server = "https://octane.um.city"
api_key = "API-TOKEN"

namespace = "/octane"

sio = socketio.Client()

def send_auth():
    sio.emit('auth', {'x-api-key': api_key}, namespace=namespace)

@sio.on('connect', namespace=namespace)
def on_connect():
    send_auth()

@sio.on('auth_ok', namespace=namespace)
def on_auth_ok(data):
    global sio
    print('\n\ngot auth ok event')
    sio.emit('join', {'channel': 'intersection'}, namespace=namespace)

@sio.on('join', namespace=namespace)
def on_join(data):
    print('Join received with ', data)

@sio.on('channels', namespace=namespace)
def on_channels(data):
    print('Channel information', data)

@sio.on('disconnect', namespace=namespace)
def on_disconnect():
    print('disconnected from server')

@sio.on('intersection_update', namespace=namespace)
def on_intersection_update(data):
    if(data['id'] == 4):
        print("\n")
        print_intersection_update(data['state']['phases'])


# prints intersection_update in viewable format
def print_intersection_update(data):
   [print(data[phase]) for phase in data if int(phase) <=8]


if not api_key:
    print("Waiting for API key")
    while not api_key:
        time.sleep(1)
    print("API key loaded, connecting")

sio.connect(server, namespaces=[namespace])
sio.wait()
