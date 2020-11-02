from datetime import datetime
from config import trails_api_key, weather_api_key
import requests
import json

# for file path fix
from os.path import dirname, join
current_dir = dirname(__file__)

def get_weather_data(latitude, longitude):
    """ 
    Gets current weather data from weather API based on given latitude/longitude.
    """
    latitude = round(latitude, 2)
    longitude = round(longitude, 2)
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast"
    params = {"locations":f"{latitude},{longitude}", "aggregateHours":"24", 
              "unitGroup":"us", "shortColumnNames":"true", "contentType":"json", 
              "key":weather_api_key, "forecastDays":"1"}
    response = requests.get(url = url, params = params)
    data_json = response.json()["locations"][f"{latitude},{longitude}"]
    weather_data = {
        "temperature"   :   data_json["currentConditions"]["temp"],
        "max_temp"      :   data_json["values"][0]["maxt"],
        "min_temp"      :   data_json["values"][0]["mint"],
        "wind_speed"    :   data_json["currentConditions"]["wspd"],
        "wind_direction":   data_json["currentConditions"]["wdir"],
        "humidity"      :   data_json["currentConditions"]["humidity"],
        "prob_of_precip":   data_json["values"][0]["pop"],
        "snow_depth"    :   data_json["values"][0]["snowdepth"],
        "cloud_cover"   :   data_json["values"][0]["cloudcover"],
        "conditions"    :   data_json["values"][0]["conditions"],
        "sunrise"       :   data_json["currentConditions"]["sunrise"][11:16],
        "sunset"        :   data_json["currentConditions"]["sunset"][11:16]
    }
    # print(weather_data)
    # with open("weather4.json", "w") as write_file:
    #     json.dump(data_json, write_file, indent=4)
    return weather_data
# get_weather_data(41.72,-74.23)

def get_trail_data(trail_id):
    """
    Gets hiking trail data based on trail_id from hiking project API.
    Add hiking_time and average trail grade key/value to trail data.
    """
    url = "https://www.hikingproject.com/data/get-trails-by-id"
    params = {"ids":trail_id, "key":trails_api_key}
    response = requests.get(url = url, params = params)
    trail_data = response.json()["trails"][0]
    trail_data["hiking_time"] = calculate_hiking_time(trail_data["length"],
                                                      trail_data["ascent"])
    trail_data["grade"] = calculate_grade(trail_data["length"],
                                          trail_data["ascent"])
    # with open("trail_data.json", "w") as write_file:
    #     json.dump(data_json, write_file, indent=4)
    return trail_data

def gear_evaluation(trail_data, weather_data):
    """
    Evaluate trail_data and weather_data and get gear that match criteria.
    Pulls in data from gear_data.json file to match with trail and weather data.
    Returns a list of attribute dictionaries with attribute description and gear.
    """
    temperature_attribute = evaluate_temperature(weather_data["temperature"])
    precipitation_attribute = evaluate_precipitation(weather_data)
    length_attribute = evaluate_length(trail_data["hiking_time"])
    elevation_attribute = evaluate_elevation(trail_data["grade"], trail_data["ascent"])
    # attributes are categories that define the trail and weather conditions
    # they are used to match up the trail/weather info with gear
    attributes = ["all", temperature_attribute, precipitation_attribute,
                  length_attribute, elevation_attribute]

    # file path fix
    file_path = join(current_dir, "./gear_data.json")

    with open(file_path) as in_file:
        gear_data_all = json.load(in_file)
    attribute_list = []      # list of attribute and gear info
    for attribute in attributes:
        for key in gear_data_all:
            if attribute == key:
                attribute_list.append(gear_data_all[attribute])
    # print(attributes_dict)
    return attribute_list

def evaluate_temperature(temperature):
    """
    Evaluates given temperature and returns a temperature category.
    """
    if temperature <= 30:
        return "freezing"
    elif 30 < temperature <= 45:
        return "cold"
    elif 45 < temperature <= 65:
        return "cool"
    elif 65 < temperature <= 80:
        return "moderate"
    elif 80 < temperature <= 90:
        return "warm"
    else:
        # temp is > 90
        return "hot"

def evaluate_precipitation(weather_data):
    if weather_data["prob_of_precip"] > 0:
        return "rain"
    else: 
        return None

def evaluate_length(hiking_time):
    """
    Evaluates trail length based on distance and elevation. 
    A hiking time > 3 hours is considered "medium"
    A hiking time > 6 hours is considered "long" 
    """
    if hiking_time > 360:
        return "long"
    elif hiking_time > 180:
        return "medium"
    else:
        return None


def calculate_hiking_time(length, elevation_change):
    """
    Calculate hiking time estimate based on Naismith's rule, uses trail
    length in miles, elevation_change in feet, and returns time in minutes.
    https://en.wikipedia.org/wiki/Naismith%27s_rule
    Naismith's rule: Allow one hour for every 3 miles (5 km) forward, plus an
    additional hour for every 2,000 feet (600 m) of ascent. The basic rule
    assumes hikers of reasonable fitness, on typical terrain, and under normal
    conditions.
    """
    # length (in miles) * 20 mins/mile + elevation_change/1000 * 30 min/1000 ft
    hiking_time = length * 20 + elevation_change * 30/1000
    return int(round(hiking_time))


def evaluate_elevation(grade, ascent):
    """
    Determine if a hike is considered steep or if it has an overall high
    elevation gain.
    """
    if grade > 10 or ascent > 750:
        return "steep"
    else:
        return None

def calculate_grade(length, ascent):
    """ Calculate average trail grade """
    distance_feet = length * 5280       # 5280 feet/mile
    grade = ascent / distance_feet      # calculate % grade 
    return round(grade * 100, 1)