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

# def build_custom_trails_list(all_trails_list, min_len, max_len, custom_difficulty):
#     '''Returns list of custom trails filtered by length and/or custom_difficulty'''
    
#     custom_trails_list = []
    
#     for trail in all_trails_list:
#         cur_trail = set_trail_by_length(trail, min_len, max_len)
#         cur_trail_2 = set_trail_by_difficulty(cur_trail, trail, custom_difficulty)
#         add_to_custom_trails_list(custom_trails_list, cur_trail_2)
    
#     return custom_trails_list   
        

# def set_min_max_length(min_length, max_length):
#     '''Returns minimum and maximum length values'''
    
#     min_len, max_len = None, None
    
#     # If there are values for min_length and max_length, set lengths
#     if min_length is not None and max_length is not None:
#         min_len, max_len = float(min_length), float(max_length)
    
#     return min_len, max_len

# def set_trail_by_length(trail, min_len, max_len):
#     '''Returns current trail if trail length falls within min_len and max_len.
#     Otherwise, returns None.'''
    
#     cur_trail = None

#     # If values for min_len and max_len were entered
#     if min_len is not None and max_len is not None:
#         # If the trail length falls within these values, then set cur_trail
#         if trail[len_idx] >= min_len and trail[len_idx] <= max_len:
#             cur_trail = trail
#         # If trail length is out of bounds, store message in cur_trail
#         else:
#             cur_trail = 'Length_out_of_bounds'
#     # If values for min_len and max_len were not entered, then set
#     # cur_trail to None
#     else:
#         cur_trail = None

#     return cur_trail


# def set_trail_by_difficulty(cur_trail, trail, custom_difficulty):
#     '''Returns current trail filtered by difficulty,'''

#     # If there were no max and min length values entered,
#     if cur_trail is None:
#         # If there is a custom_difficulty
#         if custom_difficulty is not None:
#             # If the trail's difficulty is in custom_difficulty,
#             # then set cur_trail
#             if trail[diff_idx] in custom_difficulty:
#                 cur_trail = trail
#             # Otherwise, set cur_trail to None
#             else:
#                 cur_trail = None
#         # If there is no custom_difficulty, then set cur_trail to None
#         else:
#             cur_trail = None

#     # If max and min length values were entered
#     else:
#         # If the max and min values entered were out of bounds, then set
#         # cur_trail to None
#         if cur_trail == 'Length_out_of_bounds':
#             cur_trail = None
#         # If cur_trail's length is in between entered max and min values
#         else:
#             # If there is a custom_difficulty list
#             if custom_difficulty is not None:
#                 # If the cur_trail's difficulty is not in custom_difficulty,
#                 # then set cur_trail to None
#                 if cur_trail[diff_idx] not in custom_difficulty:
#                     cur_trail = None
    
#     return cur_trail


# def add_to_custom_trails_list(custom_trails_list, cur_trail):
#     '''Appends cur_trail to custom_trails_list if cur_trail has a 
#     value.'''

#     if cur_trail is not None:
#         custom_trails_list.append(cur_trail)


# def build_custom_trails_list(all_trails_list, min_len, max_len, custom_difficulty):
#     '''Returns list of custom trails filtered by length and/or custom_difficulty'''
    
#     custom_trails_list = []
    
#     for trail in all_trails_list:
#         cur_trail = set_trail_by_length(trail, min_len, max_len)
#         cur_trail_2 = set_trail_by_difficulty(cur_trail, trail, custom_difficulty)
#         add_to_custom_trails_list(custom_trails_list, cur_trail_2)
    
#     return custom_trails_list

    # XMLpath for "trail type" at trail URL - test scraping?
    # type_path = /html/body/div[6]/div/div[2]/div[3]/div[2]/div[1]/h3