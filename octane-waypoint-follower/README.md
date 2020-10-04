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
 
 