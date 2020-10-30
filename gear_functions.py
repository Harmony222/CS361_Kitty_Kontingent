from datetime import datetime
from config import weatherAPIKey, trailsAPIKey
import requests
import json

def get_weather_data(latitude, longitude):
    """ 
    Gets current weather data from weather API based on given latitude/longitude.
    """
    url = "https://api.weather.com/v3/wx/observations/current"
    params = {"geocode":f"{latitude},{longitude}", "units":"e", "language":"en-US", "format":"json", "apiKey":weatherAPIKey}
    response = requests.get(url = url, params = params)

    data_json = response.json()
    # with open("weather.json", "w") as write_file:
    #     json.dump(data_json, write_file, indent=4)
    return data_json

def get_trail_data(trail_id):
    """
    Gets hiking trail data based on trail_id from hiking project API 
    """
    url = "https://www.hikingproject.com/data/get-trails-by-id"
    params = {"ids":trail_id, "key":trailsAPIKey}
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
    attributes = ["all", temperature_attribute]
    with open("gear_data.json") as in_file:
        gear_data_all = json.load(in_file)
    attribute_list = []
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
    pass



# trail_id = 7022927
# gear_evaluation(trail_id)
