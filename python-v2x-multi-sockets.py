"""
python-v2x-multi-sockets.py
Sample Mcity OCTANE Python script for interacting with V2X AACE data.
This utilizing Python multiprocessing to offload processing of packets
to workers in queues on other threads/processes depending on system architecture.

On Linux/Mac this is handled via fork and system threads.
On Windows it may not be supported.

Pre-requisite is installation of websocket-client and python-socketio packages.

See this link for documentation on joinable channels, events, and event payloads:
https://mcity.um.city/apidocs/#/WebSockets-Events
"""
import os
import json
import socketio #You'll want to install python-socketio and websocket-client packages using PIP
import arrow
import time
from multiprocessing import Pool


#Load environment variables
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = 'https://octane.aace.um.city/'
namespace = "/octane"
number_of_workers = 4 #Number of processes used to handle incoming data.

#If no API Key provided, exit.
if not api_key:
    print ("No API KEY SPECIFIED. EXITING")
    exit()

def process_data(type: str, data: dict):
    """ 
    Each packet processed will be run by a worker who will call this function.
    Utilize the type string to determine how to process the data dictionary.
    """
    if type == 'INT':
        print('INT 1HZ {}: ID: {} Phase {} will be {} for at least {} seconds.'.format(arrow.utcnow().format('YYYY-MM-DDTHH:mm:ssZZ'), 
            data['id'], data['state']['phases'][0]['phase'], data['state']['phases'][0]['color'], data['state']['phases'][0]['vehTimeMin']))
    elif type == 'SPAT':
        #See how far behind we are.
        diff = arrow.utcnow() - arrow.get(data['updated'])
        if diff.seconds > 2:
            print ("SPAT Drift {}".format(diff))
        #Keep process busy to simulate work
        #If you see the message above triggering, decrease work length, or increase workers
        time.sleep(.02)
        
        #print('SPAT 10hz: {} - UPDATED: {}'.format(arrow.utcnow().format('YYYY-MM-DDTHH:mm:ssZZ'), data['updated']))
    elif type == 'BSM':
        print('BSM 10hz: {} - UPDATED: {}'.format(arrow.utcnow().format('YYYY-MM-DDTHH:mm:ssZZ'), data['updated']))
    elif type == 'RAW':
        print('RAW {} - DATA {}'.format(arrow.utcnow().format('YYYY-MM-DDTHH:mm:ssZZ'), data))
    else:
        print ("UNKNWON:" + data)

def error_callback(self, err):
    """ 
    If a worker fails to process a packet, this is function will be called in the main/parent process.
    """
    print(err)

def send_auth():
    """
    Emit an authentication event.
    """
    sio.emit('auth', {'x-api-key': api_key}, namespace=namespace)

def on_connect():
    """
    Handle connection event and send authentication key
    """
    send_auth()

def on_join(data: dict):
    """
    Event fired when user joins a channel
    """
    print('Join received:', data)

def on_channels(data: dict):
    """
    Event fired when a user requests current channel information.
    """
    print('Channel information', data)
    # Parsed OBU J2735 -> JSON (10hz)
    #channel = 'v2x_obu_parsed' #BSM data -- all vehicles.
    #sio.emit('join', {'channel': channel}, namespace=namespace)

    # Parsed TSCBM SPaT data -> JSON (10hz)
    #channel = 'v2x_rsu_parsed' #SPaT data all interse
    # sio.emit('join', {'channel': channel}, namespace=namespace)

    # Single TSCBM SPaT intersection data -> JSON (10hz)
    # Get the RSU identifier from OCTANE /v2x endpoints
    # sub it for the number in the channel name below.
    # In this example we join the entire plymouth road corridor.
    channel = 'v2x_rsu_23_parsed'
    sio.emit('join', {'channel': channel}, namespace=namespace)

    channel = 'v2x_rsu_26_parsed'
    sio.emit('join', {'channel': channel}, namespace=namespace)
    
    channel = 'v2x_rsu_28_parsed'
    sio.emit('join', {'channel': channel}, namespace=namespace)
    
    channel = 'v2x_rsu_31_parsed'
    sio.emit('join', {'channel': channel}, namespace=namespace)
    
    channel = 'v2x_rsu_53_parsed'
    sio.emit('join', {'channel': channel}, namespace=namespace)

    channel = 'v2x_rsu_55_parsed'
    sio.emit('join', {'channel': channel}, namespace=namespace)

    channel = 'v2x_rsu_56_parsed'
    sio.emit('join', {'channel': channel}, namespace=namespace)
    # TSCBM SPaT RAW unparsed data (10hz)
    #channel = 'v2x_rsu_raw'
    #sio.emit('join', {'channel': channel}, namespace=namespace)

    # J2735 BSM RAW unparsed data (10hz)
    #channel = 'v2x_obu_raw'
    #sio.emit('join', {'channel': channel}, namespace=namespace)

    # Intersection channels attempts to provide (~1hz downsampled SPaT)
    # Issue a requests/get first to get the intersection IDs, then match the intersection updates
    # to the ID in the request/get to know which intersection the update is for.
    #channel = 'intersection'
    #sio.emit('join', {'channel': channel}, namespace=namespace)


def on_spat(data: dict):
    """
    Event fired for each V2X Parsed SPaT message
    """
    # Data is going to be stored in the data dictionary and can be fetched with the following syntax
    # data['walkDont']
    # 
    # To speed up how we process the data, we'll add any received packets to a queue.
    # This thread will immediately acknowledge the packet and our Asynchronous workers will handle it.
    # We share workers between SPaT and BSM in this example.
    pool.apply_async(process_data,
                    args=('SPAT', data,),
                    error_callback=error_callback)

def on_bsm(data: dict):
    """
    Event fired for each V2X RAW message
    """
    pool.apply_async(process_data,
                    args=('BSM', data,),
                    error_callback=error_callback)

def on_raw(data: dict):
    """
    Event fired for each V2X RAW message
    """
    pool.apply_async(process_data,
                    args=('RAW', data,),
                    error_callback=error_callback)

def on_int_update(data: dict):
    """
    Event fired for each Intersection update.
    Returns the OCTANE intersection ID and it's state value.
    """
    pool.apply_async(process_data,
                    args=('INTERSECTION', data,),
                    error_callback=error_callback)

def on_auth_fail(data: str):
    """
    Event fired on disconnect.
    """
    print('Failed auth, disconnecting.', data)
    print ("Shutting down workers.")
    pool.close()
    pool.join()
    exit()

def on_disconnect():
    """
    Event fired on disconnect.
    """
    print('Disconnected from OCTANE server.')
    # Reconnect on disconnect:
    sio.disconnect()
    reconnect()

def reconnect():
    #Make connection
    print ("Connecting to OCTANE via Socket.IO...")
    sio.connect(server, transports=None, namespaces=[namespace])
    print ("Connected to OCTANE!")
    sio.wait()

#Only connect in the main thread, workers will start but should not connect to Socket.IO themselves.
if __name__ == '__main__':

    print ("Created Socket.IO client")
    # Uncomment the next line if you'd like a logger showing all messages coming in and out.
    sio = socketio.Client()
    #sio = socketio.Client(logger=True, engineio_logger=True)


    pool = Pool(number_of_workers, initializer=None, initargs=(None), maxtasksperchild=10000)
    print ("Worker pool initialized")

    sio.on('disconnect', on_disconnect, namespace=namespace)
    sio.on('auth_fail', on_auth_fail, namespace=namespace)
    sio.on('connect', on_connect, namespace=namespace)
    sio.on('join', on_join, namespace=namespace)
    sio.on('channels', on_channels, namespace=namespace)
    sio.on('v2x_SPaT', on_spat, namespace=namespace)
    sio.on('v2x_BSM', on_bsm, namespace=namespace)
    sio.on('v2x_raw', on_raw, namespace=namespace)
    sio.on('intersection_update', on_int_update, namespace=namespace)

    reconnect()
    print ("Shutting down workers.")
    pool.close()
    pool.join()
    print ("Workers done, exiting")