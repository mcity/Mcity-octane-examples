import json
import requests

URL = "https://octane-tc.um.city/api/setphase"
API_KEY = "YOUR_API_KEY_HERE"

"""
Update intersection field in the payload from Intersection list below
======================
Main/Wolverine
Main/State
Main/Pontiac
Liberty/State
Liberty/Wolverine
Liberty/Pontiac
Access/Pontiac
"""

payload = {
    "intersection": "Main/Wolverine",
    "phases": [
        "phase_1_red",
        "phase_2_red", # To South
        "phase_3_red",    
        "phase_4_red",
        "phase_5_red",
        "phase_6_red", # To North
        "phase_7_red",
        "phase_8_red"
    ]
    
}

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

resp = requests.post(URL, headers=headers, json=payload, timeout=30)

print("Status:", resp.status_code)
print("Headers:", dict(resp.headers))
try:
    print("JSON:", resp.json())
except ValueError:
    print("Text:", resp.text)