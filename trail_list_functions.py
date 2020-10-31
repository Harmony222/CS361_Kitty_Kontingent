import json
import requests
from config import trails_api_key
from flask_table import Table, Col

class list_table(Table):
    '''create table object with specified info from list of trail dicts'''
    name = Col('Name')
    difficulty = Col('Difficulty')
    length = Col('Length')
    location = Col('Location')

def get_trails(lat, lon, dist):
    '''return list of trails with data within radius 'dist' from longitude/latitude'''

    base_url = "https://www.hikingproject.com/data/get-trails?lat=" + str(lat) \
                + "&lon=" + str(lon) + "&maxDistance=" + str(dist) + "&key=" + trails_api_key
    return requests.get(base_url).json()['trails']
    
    #build 
    # for trail in trails_list:

    # path for "trail type"
    # type_path = /html/body/div[6]/div/div[2]/div[3]/div[2]/div[1]/h3

    # print(base_url)
    # print(response)


get_trails(40.0274, -105.2519, 10)