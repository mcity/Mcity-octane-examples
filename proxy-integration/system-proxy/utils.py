"""
utils.py

Utility methods for accessing beacon information stored in a local redis instance.
"""
import logging
import re
import subprocess
import os
import traceback
import netifaces
import redis
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('MCITY_OCTANE_KEY', None)
server = os.environ.get('MCITY_OCTANE_SERVER', 'wss://octane.mvillage.um.city/')

GNSS_LOCATION_KEY = 'gnss:position:oxdecoder'
GNSS_SATELLITES_KEY = 'gnss:position:satellites:5'
GNSS_FIXTYPE_KEY = 'gnss:position:current:fixType:5'


class RTKUtility:
    @staticmethod
    def get_signal_strength(wireless_interface):
        cmd = 'iwconfig {} | grep Quality'.format(wireless_interface)
        result = subprocess.check_output(cmd, shell=True)
        result = re.sub(r'^.*?=', '', result.decode())
        result = re.sub(r' .*', '', result)
        return result

    @staticmethod
    def get_wifi_network(wireless_interface):
        cmd = 'iwconfig {} | grep ESSID'.format(wireless_interface)
        result = subprocess.check_output(cmd, shell=True)
        result = re.sub(r'^.*?ESSID:"', '', result.decode())
        result = re.sub(r'".*', '', result)
        return result

    @staticmethod
    def connect_beacon():
        """
        Attempt to connect to Octane and see if the Beacon has been configured

        :return: (True/False,message) True if we were able to establish a connection and the Beacon ID has been configured
        """
        headers = {'X-API-KEY': api_key}
        try:
            r = requests.get('{}/api/beacon/{}'.format(server, RTKUtility.get_device_id_clean()),
                              headers=headers, timeout=5)
            # Would be nice to distinguish page not found from no beacon in a status code
            if r.status_code == 404:
                if 'does not exist' in r.text:
                    return False, 'Unknown Beacon'
                else:
                    return False, 'Version Error'
            elif r.status_code == 403:
                return False, 'Bad Password'
            elif r.status_code != 200:
                return False, r.status_code
        except:
            logging.error(traceback.print_exc())
            return False, 'Connection Error'

        return True, 'McityOS'

    @staticmethod
    def get_device_id_clean():
        return netifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0].get('addr').replace(':','')[-6:].upper()

    @staticmethod
    def get_gps_latlong():
        r = redis.Redis(host='localhost', port=6379, db=0)
        try:
            ret_value = r.hgetall(GNSS_LOCATION_KEY)
            if ret_value:
                return ret_value.get(b'lat'), ret_value.get(b'long'), ret_value.get(b'heading'), ret_value.get(b'speed'), ret_value.get(b'machine_second')
            else:
                logging.info('No GPS location found - redis key [{}], returning 0,0'.format(GNSS_LOCATION_KEY))
                return 0, 0, 0, 0, 0
        except:
            logging.error(traceback.print_exc())
            return 0, 0, 0, 0, 0

    @staticmethod
    def get_gps_stats():
        r = redis.Redis(host='localhost', port=6379, db=0)
        try:
            gnss_info = r.get(GNSS_LOCATION_KEY).decode('utf-8')
            gnss_info = gnss_info.split(',')
            location = '{},{}'.format(gnss_info[2], gnss_info[3])

            sat_in_view = gnss_info[1]
            fixtype = r.get(GNSS_FIXTYPE_KEY).decode('utf-8')
        except:
            logging.error(traceback.print_exc())
            return None, None, None

        return location, fixtype, sat_in_view

