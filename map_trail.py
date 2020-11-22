import googlemaps
from config import directions_api_key
import json
import urllib.request

# gmaps = googlemaps.Client(directions_api_key)
GEOCODE_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DIRECTIONS_BASE_URL = "https://www.google.com/maps/dir/"
api = 1

# Geocoding an address
def get_geocode(address):
    '''Returns a geocode for an address, which is a json that contains
    multiple values, including latitude and longitude'''
    print(address)
    params = urllib.parse.urlencode({"address": address, "key": directions_api_key,})
    url = f"{GEOCODE_BASE_URL}?{params}"
    result = json.load(urllib.request.urlopen(url))
    if result['status'] in ['OK', 'ZERO_RESULTS']:
        return result['results']
    raise Exception(result['error_message'])

def get_lat_long(address):
    '''Returns the latitude and longitude from an address'''
    print(address)
    geocode_result = get_geocode(address)
    # if geocode_result:
    latitude = geocode_result[0]['geometry']['location']['lat']
    longitude = geocode_result[0]['geometry']['location']['lng']
    # else:
    # return None, None
    return latitude, longitude

def get_string(latitude, longitude):
    '''Concatenates latitude and longitude into string needed for
    directions url'''
    string_result = str(latitude) + ',' + str(longitude)
    return string_result

def get_directions_url_trails(origin_lat, origin_long, destination_lat, destination_long):
    '''Creates directions url using origin and destination longitude
    and latitudes'''
    origin = get_string(origin_lat, origin_long)
    destination = get_string(destination_lat, destination_long)
    params = urllib.parse.urlencode({"api": api, "origin": origin, "destination": destination,})
    url = f"{DIRECTIONS_BASE_URL}?{params}"
    return url