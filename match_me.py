from config import trails_api_key, weather_api_key, map_api_key
from trail_list_functions import get_trails
import requests
import json


def filter_trails(trails_list, difficulty):
    '''filters trails based on difficulty'''
    filtered_trails = []
    for trail in trails_list:
        if difficulty == trail[3]:
            filtered_trails.append(trail)
    return filtered_trails


def filtered_trail_locations(filtered_trails):
    location_list = []
    for trail in filtered_trails:
        location_list.append([str(trail[0]), trail[4], trail[5], trail[6]])
    # print("LOCATION LIST", location_list)
    return json.dumps(location_list)


def get_map_api_key():
    return map_api_key
