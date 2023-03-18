"""
mapp_common.py

Common functions and members for working with the MAPP.

"""
import socketio
import json

mapp_sio = socketio.Client()

class MAPP_Client(socketio.ClientNamespace):
    def __init__(self, api_key, server):
        self.api_key = api_key
        self.server = server
        self.namespace = "/octane"
        self.connected = False
        self.estop_sent = False
        self.disable_sent = False
        self.enable_sent = False
        self.move_distance_sent = False
        self.goal_completed = False
        self.single_waypoint_nav_sent = False
        self.channel = "robot_proxy"
        self.room = "robot"
        super().__init__(self.namespace)

    def send_auth(self):
        """
        Emit an authentication event.
        """
        print("Authenticating...")
        self.emit('auth', {'x-api-key': self.api_key}, namespace=self.namespace)

    def on_connect(self):
        """
        Handle connection event and send authentication key
        """
        print("Connected!")
        self.send_auth()


    def on_join(self, data):
        """
        Event fired when user joins a channel
        """
        print('Join received with ', data)
        if data.get('join', None) == self.room:
            self.connected = True

    def on_auth_ok(self, data):
        """
        Called when authentication is successful
        """
        print(f"Authenticated successfully, joining {self.room}")
        self.emit('join', {'channel': self.room}, namespace=self.namespace)

    def on_robot_proxy(self, data):
        """
        Print out any data received on the robot_proxy channel
        """
        # print(data)
        if str(data.get('type', None)) == 'goal_result':
            print("GOAL_COMPLETED")
            self.goal_completed = True

    def estop(self, proxy_id):
        """
        Send an estop request to the proxy.
        """
        def estop_callback():
            self.estop_sent = True
            print("Estop sent")
        self.emit(
            self.channel,
            {
                "id": proxy_id,
                "type": "estop"
            },
            namespace=self.namespace,
            callback=estop_callback
        )

    def enable(self, proxy_id):
        """
        Send an enable request to the proxy.
        """
        def enable_callback():
            self.enable_sent = True
            print("Enable sent")
        self.emit(
            self.channel,
            {
                "id": proxy_id,
                "type": "enable"
            },
            namespace=self.namespace,
            callback=enable_callback
        )

    def disable(self, proxy_id):
        """
        Send a disable request to the proxy.
        """
        def disable_callback():
            self.disable_sent = True
            print("Disable sent")
        self.emit(
            self.channel,
            {
                "id": proxy_id,
                "type": "disable"
            },
            namespace=self.namespace,
            callback=disable_callback
        )

    def cancel(self, proxy_id):
        """
        Send a cancel request to stop any currently running action.
        """
        def cancel_callback():
            self.cancel_sent = True
            print("Cancel sent")
        self.emit(
            self.channel,
            {
                "id": proxy_id,
                "type": "action",
                "cancel": True,
            },
            namespace=self.namespace,
            callback=cancel_callback
        )

    def move_distance(self, proxy_id, meters, meters_per_second):
        print(f"Sending new Move_Distance goal for ID {proxy_id} to {self.server}")
        def trigger_callback():
            self.move_distance_sent = True
            print("Message sent")
        self.emit(
            self.channel,
            {
                "id": proxy_id,
                "type": "action",
                "action": "move_distance",
                "cancel": False,
                "values": {
                    "move_distance_goal": {
                        "meters_per_second": meters_per_second,
                        "meters": meters
                    }
                }
            },
            namespace=self.namespace,
            callback=trigger_callback
        )

    def single_waypoint_nav(self, proxy_id, lat, long, meters_per_second):
        print(f"Sending new single Waypoint_Nav goal for ID {proxy_id} to {self.server}")
        def trigger_callback():
            self.single_waypoint_nav_sent = True
            print("Message sent")
        self.emit(
            self.channel,
            {
                "id": proxy_id,
                "type": "action",
                "action": "waypoint_nav",
                "cancel": False,
                "values": {
                    "waypoint_nav_goal": {
                        'waypoints': [
                            {
                                'latitude': lat,
                                'longitude': long,
                                'meters_per_second': meters_per_second
                            }
                        ]
                    }
                }
            },
            namespace=self.namespace,
            callback=trigger_callback
        )

