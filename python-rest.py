"""
python-rest.py
Sample Mcity OCTANE python rest script
"""
import os
from dotenv import load_dotenv
import requests

#Load environment variables
load_dotenv()
api_key = os.environ.get('MCITY_OCTANE_KEY', None) 
server = os.environ.get('MCITY_OCTANE_SERVER', 'http://localhost:5000')
namespace = "/octane"

#If no API Key provided, exit.
if not api_key:
    print ("No API KEY SPECIFIED. EXITING")
    exit()

#Set State/Liberty to Red
# Query /intersections to get the intersection ID. It's 1 for this light.
#
# Look at stage data on the intersection to find the non-conflicting phases for this 
# intersection. The traffic controller only lets you set holds on Green. If you want 
# to hold red, you need to hold all the other phases to green. 
# West/East is the opposite direction with Phases 4, 8.
# So we'll hold them green to get North/South red.
#
# Issue command to change light. 
#- resets all settings at this intersection
#- omits the phases we do not want green, stopping them from happening again.
#- hold the phases we want to be green (4+8)
#- force off the phases we don't want to be green, if they are presently on.

headers = {
    'accept': 'application/json',
    'X-API-KEY': api_key,
    'Content-Type': 'application/json',
}

data = '{ "state": { "reset": true, "omit": "01110111", "hold": "10001000", "forceOff": "01110111" }}'

uri = server + '/api/intersection/1'
response = requests.patch(uri, headers=headers, data=data)
print (response.text)