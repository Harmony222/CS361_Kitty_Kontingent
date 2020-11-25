from datetime import datetime, date, timedelta
from config import trails_api_key, weather_api_key, historical_weather_api_key, sun_api_key
import requests
import json

def get_sun_info(latitude, longitude, selected_date):
    """ Return sunrise and sunset times for lat/lon for selected date """
    url = "https://api.ipgeolocation.io/astronomy"
    params = {"apiKey":sun_api_key, "lat":latitude, "long":longitude,
              "date":selected_date}
    response = requests.get(url = url, params = params)
    data_json = response.json()
    sunrise = datetime.strptime(data_json["sunrise"], "%H:%M").strftime("%I:%M %p")
    sunset = datetime.strptime(data_json["sunset"], "%H:%M").strftime("%I:%M %p")
    return sunrise, sunset

def get_weather_forecast(latitude, longitude, selected_date):
    """ Gets weather data for days <= 14 days from today's date """
    # Number of days from today to selected_date
    forecast_days = (selected_date - date.today()).days + 1
    # Visual Crossing forecast API call
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast"
    params = {"locations":f"{latitude},{longitude}", "aggregateHours":"24", 
              "unitGroup":"us", "shortColumnNames":"true", "contentType":"json", 
              "key":weather_api_key, "forecastDays":f"{forecast_days}"}
    response = requests.get(url = url, params = params)
    data_json = response.json()["locations"][f"{latitude},{longitude}"]
    # Select forecast data for the selected day
    forecast = data_json["values"][forecast_days - 1]
    # get sunrise and sunset info from separate API call
    sunrise, sunset = get_sun_info(latitude, longitude, selected_date)
    weather_data = {
        "date"          :   selected_date,
        "conditions"    :   forecast["conditions"] or None,
        "temperature"   :   forecast["temp"] or None,
        "max_temp"      :   forecast["maxt"] or None,
        "min_temp"      :   forecast["mint"] or None,
        "wind_speed"    :   forecast["wspd"] or None,
        "wind_direction":   forecast["wdir"] or None,
        "humidity"      :   forecast["humidity"] or None,
        "prob_of_precip":   forecast["pop"] or None,
        "precip"        :   None,
        "snow_depth"    :   forecast["snowdepth"] or None,
        "snow_accum"    :   None,
        "cloud_cover"   :   forecast["cloudcover"] or None,
        "sunrise"       :   sunrise or None,
        "sunset"        :   sunset or None
    }
    return weather_data

def get_historical_weather(latitude, longitude, selected_date):
    """ 
    Get historical weather data if selected date > 14 days from todays' date
    """
    url = "https://api.weather.com/v3/wx/almanac/daily/5day"
    params = {"geocode":f"{latitude},{longitude}", "units":"e",
              "startDay":selected_date.day, "startMonth":selected_date.month,
              "format":"json", "apiKey":historical_weather_api_key}
    response = requests.get(url = url, params = params)
    data_json = response.json()
    sunrise, sunset = get_sun_info(latitude, longitude, selected_date)
    weather_data = {
        "date"          :   selected_date,
        "conditions"    :   None,
        "temperature"   :   data_json["temperatureMean"][0] or None,
        "max_temp"      :   data_json["temperatureAverageMax"][0] or None,
        "min_temp"      :   data_json["temperatureAverageMin"][0] or None,
        "wind_speed"    :   None,
        "wind_direction":   None,
        "humidity"      :   None,
        "prob_of_precip":   None,
        "precip"        :   data_json["precipitationAverage"][0] or None,
        "snow_depth"    :   None,
        "snow_accum"    :   data_json["snowAccumulationAverage"][0] or None,
        "cloud_cover"   :   None,
        "sunrise"       :   sunrise or None,
        "sunset"        :   sunset or None
    }
    # precipitation accumulation <= 0.1 not considered significant
    if weather_data["precip"] <= 0.1:
        weather_data["precip"] = 0
    return weather_data
    
def get_weather_data(latitude, longitude, selected_date):
    """ 
    Gets current weather data from weather API based on given latitude/longitude.
    Get forecast weather data if selected date <= 14 days from today, otherwise
    get historical weather data.
    """
    latitude = round(latitude, 2)
    longitude = round(longitude, 2)
    today = date.today()
    forecast_date = today + timedelta(days=14)
    if selected_date <= forecast_date:
        # Use Visual Crossing API call for current and forecast weather is 
        # selected date is <= 14 days from today's date
        weather_data = get_weather_forecast(latitude, longitude, selected_date)
        historical = False
    else:
        # Use Weather Company API call for historical weather if selected date
        # is greater than 14 days from today's date
        weather_data = get_historical_weather(latitude, longitude, selected_date)
        historical = True
    return weather_data, historical

def get_trail_data(trail_id):
    """
    Gets hiking trail data based on trail_id from hiking project API.
    Add hiking_time and average trail grade key/value to trail data.
    """
    url = "https://www.hikingproject.com/data/get-trails-by-id"
    params = {"ids":trail_id, "key":trails_api_key}
    response = requests.get(url = url, params = params)
    if response.status_code == 200:
        trail_data = response.json()["trails"][0]
        trail_data["hiking_time"] = calculate_hiking_time(trail_data["length"],
                                                        trail_data["ascent"])
        trail_data["grade"] = calculate_grade(trail_data["length"],
                                            trail_data["ascent"])
    else:
        trail_data = None
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
    snow_attribute = evaluate_snow(weather_data)
    length_attribute = evaluate_length(trail_data["hiking_time"])
    elevation_attribute = evaluate_elevation(trail_data["grade"], trail_data["ascent"])
    # attributes are categories that define the trail and weather conditions
    # they are used to match up the trail/weather info with gear
    attributes = ["all", temperature_attribute, precipitation_attribute,
                  snow_attribute, length_attribute, elevation_attribute]
    gear_meta_data = build_gear_meta_data()
    gear_dict = get_gear(attributes, gear_meta_data)
    return gear_dict

def evaluate_temperature(temperature):
    """
    Evaluates given temperature and returns a temperature category.
    """
    if temperature <= 30:
        return "freezing_temp"
    elif 30 < temperature <= 45:
        return "cold_temp"
    elif 45 < temperature <= 65:
        return "cool_temp"
    elif 65 < temperature <= 80:
        return "moderate_temp"
    elif 80 < temperature <= 90:
        return "warm_temp"
    else:
        # temp is > 90
        return "hot_temp"

def evaluate_precipitation(weather_data):
    if (weather_data["prob_of_precip"] and weather_data["prob_of_precip"] > 0) or \
                (weather_data["precip"] and weather_data["precip"] > 0.1):
        return "rain"
    else: 
        return None

def evaluate_snow(weather_data):
    if (weather_data["snow_depth"] and weather_data["snow_depth"] > 0) or \
                (weather_data["snow_accum"] and weather_data["snow_accum"] > 0):
        return "snow"
    else:
        return None
    
def evaluate_length(hiking_time):
    """
    Evaluates trail length based on distance and elevation. 
    A hiking time > 3 hours is considered "medium_duration"
    A hiking time > 6 hours is considered "long_duration" 
    """
    if hiking_time > 360:
        return "long_duration"
    elif hiking_time > 180:
        return "medium_duration"
    else:
        return None


def calculate_hiking_time(length, elevation_change):
    """
    Calculate hiking time estimate based on Naismith's rule, uses trail
    length in miles, elevation_change in feet, and returns time in hours.
    https://en.wikipedia.org/wiki/Naismith%27s_rule
    Naismith's rule: Allow one hour for every 3 miles (5 km) forward, plus an
    additional hour for every 2,000 feet (600 m) of ascent. The basic rule
    assumes hikers of reasonable fitness, on typical terrain, and under normal
    conditions.
    """
    # time (minutes) = length (in miles) * 20 minutes/mile 
    #                  + elevation_change (in feet) * 30 min/1000 feet
    hiking_time = length * 20 + elevation_change * 30/1000
    # convert time from minutes to hours and round to 1 decimal place
    return round((hiking_time / 60), 1)

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
    if distance_feet > 0:
        grade = ascent / distance_feet      # calculate % grade 
    else:
        grade = 0
    return round(grade * 100, 1)




"""
GEAR DATA
"""
class Gear_Item:
    """ Represents a single gear item and its category. """
    def __init__(self, item_name, category):
        self._item_name = item_name
        self._category = category
    
    def __repr__(self):
        return self._item_name

    def get_category(self):
        return self._category

    def get_gear_item(self):
        return {self._item_name : {"category" : self._category}}


class Use_Condition:
    """ 
    Represents a use condition, each use condition has a description and
    has gear items that fall under that use condition. 
    """
    def __init__(self, name, description, icon):
        self._name = name
        self._description = description
        self._icon = icon
        self._gear = {}
    
    def set_gear(self, gear_list):
        for gear_item in gear_list:
            self._gear.update(gear_item.get_gear_item())
            # self._gear.append(gear_item.get_gear_item())
    
    def get_use_condition(self):
        return {self._name : {"description" : self._description, 
                "gear" : self._gear, "icon" : self._icon}}

    def print_use_condition(self):
        print(self._name, self._description, self._gear)


def build_gear_meta_data():
    """ Build all of the gear and use condition data. """

    gloves = Gear_Item("gloves", "clothing")
    warm_jacket = Gear_Item("warm, insulated jacket", "clothing")
    warm_boots = Gear_Item("warm boots", "footwear")
    warm_hat = Gear_Item("warm hat", "clothing")
    long_underwear = Gear_Item("long underwear", "clothing")
    warm_socks = Gear_Item("warm socks", "footwear")
    waterproof_socks = Gear_Item("waterproof socks", "footwear")
    daypack = Gear_Item("daypack", "gear")
    water = Gear_Item("water", "food and water")
    rain_pants = Gear_Item("rain pants", "clothing")
    rain_jacket = Gear_Item("rain jacket", "clothing")
    snowshoes = Gear_Item("snowshoes", "footwear")
    gaiters = Gear_Item("gaiters", "clothing")
    hiking_boots = Gear_Item("hiking boots", "footwear")
    map_gps = Gear_Item("map/GPS device", "navigation")
    light_med_jacket = Gear_Item("light-medium jacket", "clothing")
    light_jacket = Gear_Item("light jacket", "clothing")
    hiking_shoes = Gear_Item("hiking shoes", "footwear")
    moisture_wicking_clothing = Gear_Item("moisture wicking clothing", "clothing")
    shorts = Gear_Item("shorts", "clothing")
    lunch = Gear_Item("lunch", "food and water")
    extra_water = Gear_Item("extra water", "food and water")
    extra_food = Gear_Item("extra food", "food and water")
    trekking_poles = Gear_Item("trekking poles", "gear")
    waterproof_shoes = Gear_Item("waterproof shoes", "footwear")
    snacks = Gear_Item("snacks", "food and water")
    sun_protecetion = Gear_Item("sun protection", "other")
    first_aid = Gear_Item("first aid kit", "other")
    hiking_sandals = Gear_Item("hiking sandals", "footwear")
    sun_hat = Gear_Item("sun hat", "clothing")
    face_mask = Gear_Item("face mask/balaclava", "clothing")
    snow_goggles = Gear_Item("snow goggles", "other")
    microspikes = Gear_Item("microspikes/crampons", "gear")


    freezing = Use_Condition("freezing_temp", "Temperature < 31 \u00b0F.", "fas fa-thermometer-empty")
    freezing.set_gear([warm_jacket, warm_boots, gloves, warm_hat, 
                       long_underwear, warm_socks, face_mask])

    cold = Use_Condition("cold_temp", "Temperature 31-45 \u00b0F.", "fas fa-thermometer-quarter")
    cold.set_gear([light_med_jacket, gloves, warm_hat, hiking_boots])

    cool = Use_Condition("cool_temp", "Temperature 46-65 \u00b0F.", "fas fa-thermometer-half")
    cool.set_gear([light_jacket, hiking_shoes])
    
    moderate = Use_Condition("moderate_temp", "Temperature 66-80 \u00b0F.", "fas fa-thermometer-three-quarters")
    moderate.set_gear([hiking_shoes, hiking_boots, moisture_wicking_clothing])

    warm = Use_Condition("warm_temp", "Temperature 81-90 \u00b0F.", "fas fa-thermometer-full")
    warm.set_gear([moisture_wicking_clothing, shorts, hiking_sandals])

    hot = Use_Condition("hot_temp", "Temperature >91 \u00b0F.", "fas fa-thermometer-full")
    hot.set_gear([moisture_wicking_clothing, shorts, hiking_sandals, sun_hat, sun_protecetion])

    all_use = Use_Condition("all", "All hikers should bring this!", "fas fa-hiking")
    all_use.set_gear([daypack, water, snacks, hiking_boots, hiking_shoes, 
                      map_gps, sun_protecetion, first_aid])

    rain = Use_Condition("rain", "Chance of rain or snow!", "fas fa-cloud-showers-heavy")
    rain.set_gear([rain_jacket, rain_pants, waterproof_socks, waterproof_shoes, 
                   gaiters])
    
    snow = Use_Condition("snow", "There is snow on the ground.", "far fa-snowflake")
    snow.set_gear([snowshoes, face_mask, snow_goggles, gaiters, microspikes])

    medium_duration = Use_Condition("medium_duration", "This will be a medium-long hike.", "fas fa-clock")
    medium_duration.set_gear([lunch, extra_water])

    long_duration = Use_Condition("long_duration", "This will be a long hike.", "fas fa-clock")
    long_duration.set_gear([lunch, extra_water, extra_food])

    steep = Use_Condition("steep", "Steep trail or high total elevation gain.", "fas fa-mountain")
    steep.set_gear([trekking_poles])

    use_conditions = {**freezing.get_use_condition(), **cold.get_use_condition(),
                      **cool.get_use_condition(), **moderate.get_use_condition(),
                      **warm.get_use_condition(), **hot.get_use_condition(),
                      **all_use.get_use_condition(), **rain.get_use_condition(),
                      **snow.get_use_condition(), **medium_duration.get_use_condition(),
                      **long_duration.get_use_condition(), **steep.get_use_condition()}
    return use_conditions


def add_gear_item(gear_dict, use_condition):
    """
    Add all gear items in a use_condition to the gear dictionary.
    """
    for gear_item in use_condition["gear"]:
        category = use_condition["gear"][gear_item]["category"]
        if gear_item not in gear_dict[category]:
            # add gear item if not already in gear_dict
            gear_dict[category].update({gear_item : [[use_condition["description"], use_condition["icon"]]]})
        else:
            # if gear item already in gear_dict, add use condition description to
            # existing gear item
            gear_dict[category][gear_item].append([use_condition["description"], use_condition["icon"]])
    return gear_dict

def get_gear(attributes, gear_meta_data):
    """
    Create a gear dictionary with gear items whose use conditions match the
    given attributes.
    """
    # gear dictionary with gear item categories as key
    gear_dict = { "clothing" : {}, "footwear" : {}, "food and water" : {},
                  "gear" : {}, "navigation" : {}, "other" : {} }
    for attribute in attributes:
        for use_condition in gear_meta_data:
            if attribute == use_condition:
                gear_dict = add_gear_item(gear_dict, gear_meta_data[use_condition])
    # with open("gear_data2.json", "w") as write_file:
    #     json.dump(gear_dict, write_file, indent=4)
    return gear_dict
