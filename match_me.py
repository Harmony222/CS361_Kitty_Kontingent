from config import trails_api_key, weather_api_key, map_api_key
from trail_list_functions import get_trails
import requests
import json

# method 1: difficulties based on fitness level
fitness_1 = {
    1: "green",
    2: "greenBlue",
    3: "blue"
}
fitness_2 = {
    1: "greenBlue",
    2: "blue",
    3: "blueBlack"
}
fitness_3 = {
    1: "blue",
    2: "blueBlack",
    3: "black"
}

# method 2: calculate difficulty (difficulty + fitness level)
difficulty_num = {
    2: "green",
    3: "greenBlue",
    4: "blue",
    5: "blueBlack",
    6: "black", 
}


def filter_trails(trails_list, difficulty, fitness):
    """
    Filters trails based on difficulty and fitness level.
    Difficulties are 1, 2, 3 for "easy and chill", "match my fitness level"
    and "challenge me". Fitness levels are 1, 2, 3.
    """
    print("filtered trails called")
    filtered_trails = []
    # method 1
    difficulty_dict = {}
    if fitness == 1:
        difficulty_dict = fitness_1
    elif fitness == 2:
        difficulty_dict = fitness_2
    elif fitness == 3:
        difficulty_dict = fitness_3

    # method 2
    filter_difficulty = difficulty_num[int(difficulty) + int(fitness)]

    # filter trails - trail[3] is eg. "green"
    for trail in trails_list:
        if filter_difficulty == trail[3]:
            filtered_trails.append(trail)
    return filtered_trails


def trail_locations(trails):
    """List of locations for map trail markers"""
    locations = []
    for trail in trails:
        # 0:name, 1:latitude, 2:longitude, 3:summary, 4:length, 5:rating, 6: difficulty, 7:location, 8:directions_url, 9:gear_url
        locations.append([trail[1], trail[10], trail[11], trail[12], trail[2], trail[4], trail[3], trail[5], trail[13], trail[14]])

    return json.dumps(locations)


def filtered_trail_locations(filtered_trails):
    location_list = []
    for trail in filtered_trails:
        location_list.append([str(trail[0]), trail[4], trail[5], trail[6]])
    # print("LOCATION LIST", location_list)
    return json.dumps(location_list)


def get_map_api_key():
    return map_api_key

def calculate_fitness(days, hours, miles, intensity):
    """calculate the user's fitness level"""
    # first get the average number of hours of physical activity per week
    avg_hours = int(days) * int(hours) // 7
    level = avg_hours
    # adjust level based off of the user's intensity when hiking
    if int(intensity) > avg_hours and avg_hours <= 3:
        level += 1
    elif int(intensity) < avg_hours and avg_hours >= 2:
        level -= 1
    # adjust level based off of the user's average length for a hike
    if int(miles) > avg_hours and level <= 3:
        level += 1
    elif int(miles) < avg_hours and level >= 2:
        level -= 1
    # ensure level is a value from 1-4
    if level <= 1:
        level = 1

    return level
