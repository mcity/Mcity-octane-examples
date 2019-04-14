# Mcity-octane-examples

Included at example scripts utilizing the Mcity OCTANE API implementation for control of the Mcity test facility.

While not all functionality is included, this repository functions as a getting started guide for utilizing parts of the API. Please refer to the latest API documentation at https://mcity.um.city/apidocs for all supported features and functionality.

Core functionality of these examples is storing your user access token (usually in an environment variable), and making requests to the API through either a http request or a Socket.IO websocket. Any language which supports either type of functionality through supporting libraries can be used to access the API.

## Servers for usage
The scripts included default to the production environment as they are targeted at users presently renting the facility. The production server is https://mcity.um.city. To acquire a production access key you must rent the Mcity test facility by scheduling through https://scheduling.um.city

Before your scheduled session, you can utilize these scripts against our test environment by making manual changes within the .html files and the env_sample (or .env) file to switch the server to https://mvillage.um.city

Mvillage is a test environment that mostly mirrors the production environment. At this time, the major difference between the two environments is that that many items will NOT have status tracked/updated and many users can be making requests (that will not be serviced) to the environment. The request notifications will be pushed via the Socket.IO instance, but will not be serviced like production would.

Mvillage for REST requests is effective for verifying message format is correct and seeing what sample responses could look like. 
Mvillage for Socket.IO is effective for verifying connection, authentication, subscription, request notifications, and all interaction on the USER channel. The socket.IO instance does not provide responses to request or live updates similar to the REST request Mvillage environment.

## Documentation
Documentation of the entire application and a test interface is available here: https://mcity.um.city/apidocs
You can utilize the documentation interface to submit specific requests, or generate a cURL command to run from a terminal.

## Repository Structure

jquery-socketio.html - Sample jquery application that runs requests and handles/parses responses.
jQuery-rest.html - Sample jquery application that makes requests through the REST interface
python-socketio.ipynb - A Jupyter notebook containing python code equivalent to the jQuery SocketIO example 
python-rest.ipynb - A Jupyter notebook containing python code equivalent to the jQuery REST example.
python-socketio.py - A very basic SocketIO client that handles authentication.
python-rest.py - A very basic Python script executing a few calls to the REST API.


## Installation
### Clone the package
git clone https://github.com/mcity/Mcity-octane-examples.git

### jQuery examples
Run HTML page directly in browser and view the code while running each example.

### Python examples
Copy env_sample to .env file in your directory

```sh
$ cp env_sample .env
```

Insert your access token into the .env file.

```sh
$ vi .env
```

Create a virtual environment
```sh
$ python3 -m venv venv
$ source venv/bin/activate
```

Install required packages
```sh
$ pip install -r requirements.txt
```

Start Jupyter Notebooks
```sh
$ jupyter notebook
```

Start scripts
```sh
$ python socketio-example.py
```

### Development

If you'd like to contribute to this repository, please create a pull request for features or fixes. Questions can be directed to mcity-engineering@umich.edu