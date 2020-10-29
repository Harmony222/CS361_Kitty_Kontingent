from datetime import datetime
from credentials import weatherAPIKey, trailsAPIKey
import requests
import json

def get_weather_data(latitude, longitude):

    url = "https://api.weather.com/v3/wx/observations/current"
    params = {"geocode":f"{latitude},{longitude}", "units":"e", "language":"en-US", "format":"json", "apiKey":weatherAPIKey}
    response = requests.get(url = url, params = params)

    data_json = response.json()
    # with open("weather.json", "w") as write_file:
    #     json.dump(data_json, write_file, indent=4, sort_keys=True)
    return data_json

# get_weather_data(47.2529, -122.4443)


def get_trail_data(trail_id):
    url = "https://www.hikingproject.com/data/get-trails-by-id"
    params = {"ids":trail_id, "key":trailsAPIKey}
    response = requests.get(url = url, params = params)
    data_json = response.json()
    # with open("trail_data.json", "w") as write_file:
    #     json.dump(data_json, write_file, indent=4)
    return data_json