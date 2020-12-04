from config import trails_api_key
from map_trail import get_directions_url_trails
import json
import requests
# import math
from math import sin, cos, sqrt, atan2, radians, inf, asin
import haversine as hs

def get_trails(lat, lon, dist):
    '''return list of trails with data within radius 'dist' from longitude/latitude
    id, name, length, difficulty, starVotes, location, url, imgMedium, high, low, latitude, longitude, summary'''

    # url call to API
    base_url = "https://www.hikingproject.com/data/get-trails?lat=" + str(lat) \
                + "&lon=" + str(lon) + "&maxDistance=" + str(dist) + "&key=" + trails_api_key + "&maxResults=100"
    
    # check for results, get dict of trail dicts if there are any
    req = requests.get(base_url).json()
    trails_list = []
    if 'trails' in req:
        trails = requests.get(base_url).json()['trails']
    else:
        return trails_list

    # get desired trail info from dicts and create trails list
    for trail in trails:
        # "as the crow flies" distance - road distance would need an API call for every trail
        distance = get_straight_distance(lat, lon, trail['latitude'], trail['longitude'])

        # Get directions url
        directions_url = get_directions_url_trails(lat, lon, trail['latitude'], trail['longitude'])

        # to navigate to gear page
        gear_url = "/gear?trail_id=" + str(trail["id"])

        # Checks if trail summary or difficulty need to be changed
        missing = ['', 'Needs Summary', 'missing']
        if trail['summary'] in missing: trail['summary'] = '\n'
        if trail['difficulty'] in missing: trail['difficulty'] = 'dblack'

        # sets with trail info appended to list
        trails_list.append((trail["id"], trail['name'], trail['length'], trail['difficulty'], trail['stars'],
                            trail['location'], trail['url'], trail['imgMedium'], trail['high'], trail['low'],
                            trail['latitude'], trail['longitude'], trail['summary'], 
                            directions_url, gear_url, distance))
    
    return trails_list


def get_custom_trails(all_trails_list, min_length, max_length, difficulty):
    '''Returns custom list of trails with optional search values'''
    # fix values from call
    min_length = float(min_length)    
    if max_length:
         max_length = float(max_length)
    else:
        max_length = inf
    if difficulty:
        custom_difficulty = set_custom_difficulty(difficulty)
    else:
        custom_difficulty = ['green', 'greenBlue', 'blue', 'blueBlack', 'black', 'dblack']
    
    # start filtering trails
    custom_trails_list = []
    for trail in all_trails_list:
        if (trail[2] >= min_length) and (trail[2] <= max_length) and (trail[3] in custom_difficulty):
            custom_trails_list.append(trail)

    return custom_trails_list

def set_custom_difficulty(difficulty):
    '''Returns a custom difficulty list that corresponds to original difficulty value'''

    # set appropriate custom_difficulty list
    if difficulty == 'Easy':
        custom_difficulty = ['green', 'greenBlue']
    elif difficulty == 'Medium':
        custom_difficulty = ['blue', 'blueBlack']
    else:
        custom_difficulty = ['black', 'dblack']
    
    return custom_difficulty

def get_straight_distance(lat1, lon1, lat2, lon2):
    '''calculates straight distance between two points in miles'''

    # # make sure all variables are floats for conversion, then convert
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])

    # math is too hard, use libraries
    # converts haversine to miles
    loc1, loc2 = (lat1, lon1), (lat2, lon2)
    dist = round(hs.haversine(loc1, loc2) * 0.621371192, 2)

    return dist