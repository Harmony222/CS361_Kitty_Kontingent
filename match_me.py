from config import trails_api_key, weather_api_key, map_api_key
from trail_list_functions import get_trails
import requests
import json


def filter_trails(trails_list, difficulty):
    trails_list = get_trails(47.60621, -122.3321, 100)
    filtered_trails = []
    for trail in trails_list:
        filtered_trails.append((trail['name'], trail['difficulty'], trail['length'],
                                trail['location'], float(trail['latitude']), float(trail['longitude'])))
    return filtered_trails


def filtered_trail_locations(filtered_trails):
    location_list = []
    for trail in filtered_trails:
        location_list.append([str(trail[0]), trail[4], trail[5], 0])
    print("LOCATION LIST", location_list)
    return json.dumps(location_list)


def get_map_api_key():
    return map_api_key