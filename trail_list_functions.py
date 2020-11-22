import json
import requests
from config import trails_api_key
from map_trail import get_directions_url_trails
import math

len_idx = 2
diff_idx = 3

def get_trails(lat, lon, dist):
    '''return list of trails with data within radius 'dist' from longitude/latitude
    id, name, length, difficulty, starVotes, location, url, imgMedium, high, low, latitude, longitude, summary'''

    base_url = "https://www.hikingproject.com/data/get-trails?lat=" + str(lat) \
                + "&lon=" + str(lon) + "&maxDistance=" + str(dist) + "&key=" + trails_api_key + "&maxResults=100"
    
    # return requests.get(base_url).json()['trails'] 
    # dict of trail dicts
    trails = requests.get(base_url).json()['trails']
    trails_list =[]
    for trail in trails:
        # Get directions url
        directions_url = get_directions_url_trails(lat, lon, trail['latitude'], trail['longitude'])
        gear_url = "/gear?trail_id=" + str(trail["id"])
        # sets with trail info appended to list
        trails_list.append((trail["id"], trail['name'], trail['length'], trail['difficulty'], trail['stars'],
                            trail['location'], trail['url'], trail['imgMedium'], trail['high'], trail['low'],
                            trail['latitude'], trail['longitude'], trail['summary'], directions_url, gear_url))
    
    return trails_list


def get_custom_trails(all_trails_list, min_length, max_length, difficulty):
    '''Returns custom list of trails with optional search values'''
    # fix values from call
    min_length = float(min_length)    
    if max_length:
         max_length = float(max_length)
    else:
        max_length = math.inf
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
