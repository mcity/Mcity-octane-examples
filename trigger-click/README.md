# OCTANE Trigger Click

These script demonstrate reacting to IPC Trigger events in OCTANE, and broadcasting proxy state to anyone listening.

Specifically this script will wait for a trigger event from a given device and then click a specified location on the screen when it occurs. This provides the start of a framework for integrating systems which only provide a GUI interface for activation.

## Installation

```sh
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt 
```

## From the System Under Test side

Here we want two things: the position of the proxy, and the ability to trigger the proxy to begin its scenario. For the 
position, we'll use the `proxy-location.py` script. You can run it like this:

```commandline
$ export MCITY_OCTANE_KEY=somekey
$ export MCITY_OCTANE_SERVER="wss://octane.mvillage.um.city"
$ python trigger-click/system-under-test/proxy-location.py 
```

This will print out the location of the proxy as updates are received. For triggering the proxy, call:

```commandline
$ export MCITY_OCTANE_KEY=somekey
$ export MCITY_OCTANE_SERVER="wss://octane.mvillage.um.city"
$ export MCITY_BEACON_ID=1
$ python trigger-click/system-under-test/trigger-proxy.py
```

## From the Proxy side

For the proxy (VRU, soft vehicle, etc), we want to listen for trigger requests, and provide position updates. To listen 
for trigger requests, we can use this click script, which will click a "Go" button in the proxy software when a
trigger request is received:

```commandline
$ # args are OCTANE_SERVER API_TOKEN TRIGGER_TYPE TRIGGER_ID X Y
$ python trigger-click/system-proxy/trigger-click.py trigger https://octane.mvillage.um.city somekey SOFTWARE 1 0 0
```

To provide position updates, we can either use an Mcity RTK beacon, or Mcity's Oxdecoder, which translates Oxford
RTK packets into beacon updates for Mcity OS to use. Either way, to let Mcity OS know the position:

```commandline
$ export MCITY_OCTANE_KEY=somekey
$ export MCITY_OCTANE_SERVER="wss://octane.mvillage.um.city"
$ export MCITY_BEACON_ID=1
$ python trigger-click/system-proxy/publish-proxy-location.py
```
### Running the trigger-click.py script

Other options are available for the trigger script:
```sh Known position
$ python3 trigger-click.py trigger OCTANESERV OCTANEKEY TRIGGERTYPE TRIGGERID Xpos Ypos
```

```sh Interactive position picking
$ python3 trigger-click.py trigger OCTANESERV OCTANEKEY TRIGGERTYPE TRIGGERID Xpos Ypos --xy-picker
```
