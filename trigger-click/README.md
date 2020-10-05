# OCTANE Trigger Click

This script demonstrates reacting to IPC Trigger events in OCTANE.

Specifically this script will wait for a trigger event from a given device and then click a specified location on the screen when it occurs. This provides the start of a framework for integrating systems which only provide a GUI interface for activation.

## Installation

```sh
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt 
```

## Running

```sh Known position
$ python3 trigger-click.py trigger OCTANESERV OCTANEKEY TRIGGERTYPE TRIGGERID Xpos Ypos
```

```sh Interactive position picking
$ python3 trigger-click.py trigger OCTANESERV OCTANEKEY TRIGGERTYPE TRIGGERID Xpos Ypos --xy-picker
```
