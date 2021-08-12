# Octane Waypoint Follower

This script demonstrates a simple GeoJSON-based waypoint follower, which will broadcast a 
J2735 BSM/PSM trail as it traverses a path. You can use any GeoJSON editor to draw a path 
(LineString or MultiPoint.) See for example [geojson.io](http://geojson.io/).

## Installation

```sh
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt 
```

## Running

* Create a [GeoJSON](https://geojson.org/) file with an [editor of your choice](https://duckduckgo.com/?q=geojson+editor), containing a single LineString or MultiPoint object.
* Obtain credentials for the OCTANE instance at your facility (or test instance.)
* Run `follow-path.py`: 
    ```sh
    $ ./follow-path.py my-geojson-path.json
    ```
 * Take a look at the corresponding Skyline instance (usually swap out octane for skyline in the url) and you should see your virtual person / vehicle move along your path. If supported by your installation, V2X messages are being broadcast!

### Running Multiple OBUs

This feature is in its infancy, but works out of the box to create multiple moving OBUs to any octane server. It is configured to:
* follow the aroundMCity.json path
* send obu messages
* move at a speed of 10
* send messages to the mvillage server
* create as many obus as you can make unique ids of (don't suggest doing too many at once, you'll get kicked out of octane)

To run the generator use the command:
```
./make-followers.sh <id-1> <id-2> <id-3> ... <id-x>
```
Where each id is some unique eight digit alphanumeric string, and each id corresponds to one OBU to create. For simplicity you can use the pattern:
```
./make-followers.sh 11111111 22222222 33333333 44444444 ...
```

Ctrl+C won't kill all your processes though. You have to run the following bash script to do so:
```
./kill-all-followers.sh
```

Making this process better would be great if you want to! I made this functionality to get to testing/solving a different problem, so it's not a great interface/implementation right now, but with a little work it definitely could be :). Or if you want to use it for a quick test of something too I hope it does its job!
