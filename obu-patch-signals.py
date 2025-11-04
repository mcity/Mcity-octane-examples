"""
obu-patch-signals.py
Author: vincebel
Purpose: Coordinates intersection holds in accordance with an Mcity team's scenario route
Version: 2
Date: December 6, 2023
"""
import os
import requests
import time
import json
import geopy.distance
from datetime import datetime

API_KEY = "" # Populate with your own Mcity OS token
SERVER = "https://octane.um.city"

OBU_ID = "56026" # Populate with your OBU's ID as shown in Mcity OS
OBU_POLL_FREQ = 0.3

#If no API Key provided, exit.
if not API_KEY:
    print ("No API KEY SPECIFIED. EXITING")
    exit()


def hold_intersection(intersection_id, stage_id):
#    return # SAFETY

    headers = {
        'accept': 'application/json',
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }

    data = {
        "state": {
            "reset": True,
            "hold": str(stage_id)
        }
    }
    json_data = json.dumps(data)

    url = SERVER + '/api/intersection/' + str(intersection_id)

    response = requests.patch(url, data=json_data, headers=headers)
    print("Intersection " + str(intersection_id) + " hold: " + str(response))
   

# To be used for preliminary holds, ensure intersections are ready for run
def verify_hold(intersection_id, desired_hold_phases):
    headers = {
        'accept': 'application/json',
        'X-API-KEY': API_KEY,
    }

    url = SERVER + '/api/intersection/' + str(intersection_id)
 
    print("Validating hold for intersection #" + str(intersection_id) + "...")   
    while True:
        response = requests.get(url, headers=headers)

        intersection_data = json.loads(response.text)

        try:
            current_hold_phases = intersection_data['intersection']['state']['hold']
        except KeyError as e:
            print(f"KeyError: {e} not found.")
            current_hold_phases = []

        if current_hold_phases == desired_hold_phases:
            print("OK")
            return

        print("Error: Unable to validate hold for intersection #" + str(intersection_id) + ", trying again...")
        time.sleep(0.5)


def await_obu_proximity(target_lat, target_lon, distance_meters, point_name):
    target_point = (target_lat, target_lon)

    headers = {
        'accept': 'application/json',
        'X-API-KEY': API_KEY,
    }

    url = SERVER + '/api/v2x/obu/' + OBU_ID

    while True:
        # Get OBU distance
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("OBU not found. Check ID? (You have: " + str(OBU_ID) + ")")

        else:
            obu_data = json.loads(response.text)

            #obu_data = json.loads("""{"obu": {"id": 56026, "state": {"angle": 190.5, "elevation": 233.4, "heading": 103.4, "latitude": 42.2990703, "longitude": -83.6993815, "updated": "2023-07-27T14:58:47+00:00"}}}""") # Sample data

            obu_lat = obu_data['obu']['state']['latitude']
            obu_lon = obu_data['obu']['state']['longitude']
            obu_point = (obu_lat, obu_lon)

            obu_distance = geopy.distance.geodesic(target_point, obu_point).m
            print("OBU distance from " + point_name + " (meters): " + str(obu_distance))
       
            if obu_distance < distance_meters:
                print(point_name + " reached")
                return

        time.sleep(OBU_POLL_FREQ)


def calculate_duration(start_time, end_time):
    time_format = "%Y-%m-%d %H:%M:%S"

    datetime1 = datetime.strptime(start_time, time_format)
    datetime2 = datetime.strptime(end_time, time_format)

    time_difference = datetime2 - datetime1

    return time_difference.total_seconds()


def initial_holds():
    # Static
    hold_intersection(1, 2) # Liberty / State
    hold_intersection(6, 1) # Main / Pontiac
    hold_intersection(7, 3) # Liberty / Pontiac
    hold_intersection(9, 2) # South Ramp
    hold_intersection(10, 1) # Entrance

    # Multi-pass (these will change)
    hold_intersection(2, 1) # Liberty / Wolverine
    hold_intersection(3, 2) # Main / Wolverine
    hold_intersection(4, 4) # Main / State


def verify_initial_holds():
    verify_hold(1, "00100010")
    verify_hold(6, "00100010")
    verify_hold(7, "10000000")
    verify_hold(10, "10001000")
    verify_hold(2, "00100010")
    verify_hold(3, "10001000")
    verify_hold(4, "00100010")


def scenario_setup():
    print("=============== Setting up scenario ===============")
    response = input("Would you like to hold the intersections?" + " (Y/N): ").strip().lower()
    if response in ('y', 'yes'):
        # Initial holds for all relevant intersections
        initial_holds()

        # Verify initial holds are in effect before running scenario
        verify_initial_holds()

    return 


def test_loop():

    print("\n================ Starting scenario ================")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # P1, Main / State
    await_obu_proximity("42.300779", "-83.698691", 7, "P1")
    hold_intersection(4, 2)

    # P2, Main / State
    await_obu_proximity("42.300894", "-83.698477", 7, "P2")
    hold_intersection(4, 4)

    # P3, Main / Wolverine
    await_obu_proximity("42.300779", "-83.697981", 7, "P3")
    hold_intersection(3, 1)

    # P4, Liberty / Wolverine
    await_obu_proximity("42.300686", "-83.697980", 7, "P4")
    hold_intersection(2, 2)

    # P5, Liberty / Wolverine
    await_obu_proximity("42.300281", "-83.697982", 7, "P5")
    hold_intersection(2, 1)

    # P6, Liberty / Wolverine
    await_obu_proximity("42.300498", "-83.697897", 7, "P6")
    hold_intersection(2, 2)

    # P7, Main / State
    await_obu_proximity("42.300779", "-83.698691", 7, "P7")
    hold_intersection(4, 2)

    # P8, Reset all
    await_obu_proximity("42.300874", "-83.697802", 7, "P8")
    initial_holds() # Reset intersections ASAP (for repeatable testing)

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n================== Test complete ==================")
    print("Time elapsed: " + str(calculate_duration(start_time, end_time)) + " seconds\n")


# Main
scenario_setup()

while True:
  test_loop()

