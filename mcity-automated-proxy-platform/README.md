# Mcity Automated Proxy Platform (MAPP) Examples

In order to make use of these examples, ensure that you have the Python SocketIO client v4.x installed:

```
pip install 'python-socketio==5.8.0'
```

Also, set the following environment variables:

| Variables           | Description                                                                                                     |
|---------------------|-----------------------------------------------------------------------------------------------------------------|
| `MCITY_OCTANE_KEY`    | This will be either your Mcity Token provided with your reservation, or the default token if using Mvillage.    |
| `MCITY_OCTANE_SERVER` | The url of the server you plan to connect to (for instance, `wss://octane.um.city` or `wss://octane.mvillage.um.city`) |
| `MCITY_ROBOT_ID` | The ID of the specific Robot you wish to communicate with. |
