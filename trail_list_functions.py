import json
import requests
from config import trails_api_key
from map_trail import get_directions_url_trails

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
        # sets with trail info appended to list
        trails_list.append((trail["id"], trail['name'], trail['length'], trail['difficulty'], trail['starVotes'],
                            trail['location'], trail['url'], trail['imgMedium'], trail['high'], trail['low'],
                            trail['latitude'], trail['longitude'], trail['summary'], directions_url))
    
    return trails_list


    # XMLpath for "trail type" at trail URL - test scraping?
    # type_path = /html/body/div[6]/div/div[2]/div[3]/div[2]/div[1]/h3