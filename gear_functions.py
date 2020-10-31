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
    Gets hiking trail data based on trail_id from hiking project API 
    """
    url = "https://www.hikingproject.com/data/get-trails-by-id"
    params = {"ids":trail_id, "key":trails_api_key}
    response = requests.get(url = url, params = params)
    data_json = response.json()
    # with open("trail_data.json", "w") as write_file:
    #     json.dump(data_json, write_file, indent=4)
    return data_json

def gear_evaluation(trail_data, weather_data):
    """
    Evaluate trail_data and weather_data and get gear that match criteria.
    Pulls in data from gear_data.json file to match with trail and weather data.
    Returns a list of attribute dictionaries with attribute description and gear.
    """
    temperature_attribute = evaluate_temperature(weather_data["temperature"])
    precipitation_attribute = evaluate_precipitation(weather_data)
    # attributes are categories that define the trail and weather conditions
    # they are used to match up the trail/weather info with gear
    attributes = ["all", temperature_attribute, precipitation_attribute]

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


# trail_id = 7022927
# gear_evaluation(trail_id)
