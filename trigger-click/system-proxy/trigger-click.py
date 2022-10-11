"""
trigger-click.py
Click a location on the screen when a trigger is activated in OCTANE.
"""
import sys

import arrow
import click
import pyautogui
import socketio

# Default Globals - Don't change, provide via command line.
global_api_token = 'reticulatingsplines'
global_continuous_click = True
global_x_click = 0
global_y_click = 0
global_trigger_type = 'SOFTWARE'
global_trigger_id = '0'
namespace = "/octane"    

sio = socketio.Client()


def send_auth():
    """
    Emit an authentication event.
    """
    sio.emit('auth', {'x-api-key': global_api_token}, namespace=namespace)


#Define event callbacks
@sio.on('connect', namespace=namespace)
def on_connect():
    """
    Handle connection event and send authentication key
    """
    send_auth()


@sio.on('join', namespace=namespace)
def on_join(data: dict):
    """
    Event fired when user joins a channel
    """
    #print('Subscribed to:', data)
    pass


@sio.on('channels', namespace=namespace)
def on_channels(data: dict):
    """
    Event fired when a user requests current channel information.
    """
    channel = 'ipc'
    sio.emit('join', {'channel': channel}, namespace=namespace)


@sio.on('ipc_message', namespace=namespace)
def on_ipc(data: dict):
    """
    Event fired for each ipc message.
    """
    print("Received: ", data)
    if data.get('type', None) != 'TRIGGER':
        print("Ignoring type ", data.get('type', None))
        return

    #ON Trigger do something...
    payload = data.get('payload', None)
    if not payload:
        print("Ignoring payload ", data.get('payload', None))
        return

    id = payload.get('id', None)
    type = payload.get('triggerType')
    state = payload.get('state', None)
    activated = False
    if payload.get('state', None):
        activated = payload.get('state').get('activated', False)
    if activated and type == global_trigger_type and id == int(global_trigger_id):
        try:
            pyautogui.moveTo(int(global_x_click), int(global_y_click), duration=0)
            pyautogui.click(clicks=1, button='left')
        except:
            print ("Failed to move the mouse, does this application have the required permissions?")

        print("{}:{}\n".format(arrow.utcnow().format('YYYY-MM-DDTHH:mm:ssZZ'), data), end="")
        if not global_continuous_click:
            #Exit after one click
            sio.disconnect()
            raise Exception("Exit after single trigger activation.")
    else:
        print("Ignoring activated: ", activated, type, id, global_trigger_type, int(global_trigger_id))


@sio.on('auth_fail', namespace=namespace)
def on_auth_fail(data: str):
    """
    Event fired on disconnect.
    """
    print('Failed auth', data)


@sio.on('disconnect', namespace=namespace)
def on_disconnect():
    """
    Event fired on disconnect.
    """
    print('disconnected from server')


@click.group()
def cli_click():
    pass

@cli_click.command()
@click.argument('octane-server')
@click.argument('api-token')
@click.argument('trigger-type')
@click.argument('trigger-id')
@click.argument('x')
@click.argument('y')
@click.option('--xy-picker/--no-xy-picker', default=False, help='Interactive screen location picker, override X and Y '
                                                                'position.')
@click.option('--continuous/--no-continuous', default=True, help='Each time the trigger fires, this application will '
                                                                 'click. Specifying this option as false will cause '
                                                                 'the application to exit after one click.')
def trigger(octane_server='https://octane.mvillage.um.city', api_token='reticulatingsplines', trigger_type='SOFTWARE',
            trigger_id='SOFTWARE', x=0, y=0, xy_picker=False, continuous=True):
    """When a specific OCTANE trigger is sent, click a location on the screen.
    OCTANE_SERVER - OCTANE server instance
    API_TOKEN - OCTANE API token
    TRIGGER_TYPE - Type of Trigger to watch for SOFTWARE, LIDAR, BUTTON, etc
    X - X location to click.
    Y - Y location to cluck.
    """

    # Set the global variables from inputs.
    global global_api_token
    global global_continuous_click
    global global_x_click
    global global_y_click
    global global_trigger_type
    global global_trigger_id

    if xy_picker:
        print("Move your mouse to the desired clicking location and press CTRL-C to choose that position.")
        current_pos = pyautogui.position()
        while True:
            try:
                current_pos = pyautogui.position()
                print('\bPosition: {}'.format(current_pos), end='\r')
                sys.stdout.flush()
            except KeyboardInterrupt:
                break
        global_x_click = current_pos.x
        global_y_click = current_pos.y       
    else:
        global_x_click = x
        global_y_click = y

    global_api_token = api_token
    global_continuous_click = continuous
    global_trigger_type = trigger_type.lower()
    global_trigger_id = trigger_id

    print("Detected resolution {}".format(pyautogui.size()))
    print("Starting OCTANE connection. Will wait for {} trigger of id {}".format(trigger_type, trigger_id))
    print('Trigger Click will click location X {}, Y {} on trigger'.format(global_x_click, global_y_click))

    # Make connection to OCTANE and wait for events.
    sio.connect(octane_server, transports=None, namespaces=[namespace])
    sio.wait()
    exit()


cli = click.CommandCollection(sources=[cli_click])
if __name__ == '__main__':
    cli()
