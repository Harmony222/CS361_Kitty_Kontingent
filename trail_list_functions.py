import json
import requests
from config import trails_api_key

# temp use for lazy tables - generates basic HTML for tables
from flask_table import Table, Col

class list_table(Table):
    '''create table object with specified info from list of trail dicts
    uses dict key to reference column and places data'''
    name = Col('Name')
    difficulty = Col('Difficulty')
    length = Col('Length')
    location = Col('Location')

def get_trails(lat, lon, dist):
    '''return list of trails with data within radius 'dist' from longitude/latitude'''

    base_url = "https://www.hikingproject.com/data/get-trails?lat=" + str(lat) \
                + "&lon=" + str(lon) + "&maxDistance=" + str(dist) + "&key=" + trails_api_key
    
    # list of dicts with trail data
    return requests.get(base_url).json()['trails']


    # XMLpath for "trail type" at trail URL - test scraping?
    # type_path = /html/body/div[6]/div/div[2]/div[3]/div[2]/div[1]/h3