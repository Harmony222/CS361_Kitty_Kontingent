from config import trails_api_key, weather_api_key, map_api_key
from trail_list_functions import get_trails
import requests
import json

# desired difficulty = feeling selection + fitness level
difficulty_num = {
    2: "green",
    3: "greenBlue",
    4: "blue",
    5: "blueBlack",
    6: "black",
    7: "dblack"
}


def filter_trails(trails_list, feeling, fitness):
    """
    Filters trails based on feeling selection and fitness level.
    Feelings are 1, 2, and 3 for "easy and chill", "match my fitness level"
    and "challenge me!". Fitness levels are 1-4.
    """
    filtered_trails = []
    filter_difficulty = difficulty_num[int(feeling) + int(fitness)]

    # filter trails - trail[3] is eg. "green"
    for trail in trails_list:
        if filter_difficulty == trail[3]:
            filtered_trails.append(trail)
    return filtered_trails


def trail_locations(trails):
    """
    Returns a list of trails data for map trail markers.
    Data is formatted for the map javascript code.
    """
    locations = []
    for trail in trails:
        # 0:name, 1:latitude, 2:longitude, 3:summary, 4:length,
        # 5:rating, 6: difficulty, 7:location, 8:directions_url, 9:gear_url
        locations.append([trail[1], trail[10], trail[11], trail[12], trail[2],
                          trail[4], trail[3], trail[5], trail[13], trail[14]])

    return json.dumps(locations)


def get_map_api_key():
    return map_api_key
