from flask import Flask, render_template, request, redirect, url_for, flash
from gear_functions import get_weather_data, get_trail_data, gear_evaluation
from trail_list_functions import get_trails
from match_me import filter_trails, trail_locations, get_map_api_key
from map_trail import get_directions_url, get_lat_long
from forms import LoginForm
import webbrowser
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
import models
migrate = Migrate(app, db)

## TRAIL LIST STRUCTURE RETURNED BY GET_TRAILS(LAT, LONG, RAD) - BY INDEX REFERENCE
## 0-id, 1-name, 2-length, 3-difficulty, 4-starVotes, 5-location, 6-url, 7-imgMedium 
## 8-high, 9-low, 10-latitude, 11-longitude, 12-summary, 13-directions_url, 14-gear_url

@app.route('/')
def index():
    return render_template('index.html', active={'index':True})

all_trails_list = []
@app.route('/find_trails', methods= ['GET', 'POST'])
def find_trails():
    '''find trails page to display table with trail data'''
    global all_trails_list
    # if user has entered trail search location data
    if request.method == 'POST':
        map_api_key = get_map_api_key()
        rad, addr = request.form['rad'], request.form['address']
        lat, long = get_lat_long(addr)
        all_trails_list = get_trails(lat, long, rad)
        locations = trail_locations(all_trails_list)
        active_tab = 'list'
        if "active-tab" in request.form:
            active_tab = request.form['active-tab']
        # check for filter or a cleared filter for original list
        if "filter-slider" not in request.form or "clear" in request.form:
            return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails': True},
                                   trails_list=all_trails_list, radius=rad, address=addr, filtered=False,
                                   map_api_key=map_api_key, lat=lat, lon=long, locations=locations, view_tab=active_tab)

        # filter trails
        else:
            # filter trails on slider value
            trails_list = filter_trails(all_trails_list, request.form["filter-slider"], 2)
            locations = trail_locations(trails_list)
            return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails': True},
                                       trails_list=trails_list, radius=rad, address=addr, filtered=True,
                                       map_api_key=map_api_key, lat=lat, lon=long, locations=locations, view_tab=active_tab)
    # else render page asking for data
    else:
        return render_template('find_trails_get.html', title='Find Hiking Trails', active={'find_trails': True})


@app.route('/map_trail', methods=['GET', 'POST'])
def map_trail():
    '''Gets start and trail addresses then opens new tab with google
    maps directions from start to trail address'''
    if request.method == 'POST':
        start_address = request.form['start-loc']
        trail_address = request.form['trail-loc']
        directions_url = get_directions_url(start_address, trail_address)
        return render_template('map_trail.html', title='Map Trail', active={'map_trail':True}), webbrowser.open_new_tab(directions_url)
    
    else:
        return render_template('map_trail.html', title='Map Trail', active={'map_trail':True})


@app.route('/match_me')
def match_me():
    lat, lon, dist = 47.60621, -122.3321, 100
    all_trails = get_trails(lat, lon, dist)
    # filtered_trails = filter_trails(all_trails, 2, 2)
    locations = trail_locations(all_trails)
    map_api_key = get_map_api_key()
    return render_template('match_me.html', title='Match Me With A Trail',
                           active={'match_me': True}, map_api_key=map_api_key,
                           all_trails=all_trails, locations=locations, lat=lat, lon=lon)

                           # filtered_trails=filtered_trails,
                           # locations=locations, lat=lat, lon=lon,
                           # filter_trails_func=filtered_trails)


@app.route('/gear', methods=["GET"])
def gear():
    if request.method == "GET" and request.args:
        trail_id = request.args["trail_id"]
    else:
        trail_id = 7011192
    trail_data = get_trail_data(trail_id)
    if trail_data:
        weather_data = get_weather_data(trail_data["latitude"], 
                                        trail_data["longitude"])
        gear_data = gear_evaluation(trail_data, weather_data)
    else:
        weather_data, gear_data = None, None
    return render_template('gear.html', title='Find Hiking Gear', 
                            active={'gear':True}, weather_data=weather_data,
                            trail_data=trail_data, 
                            gear_data=gear_data)

@app.route('/my_info', methods=["GET"])
def my_info():
    if request.method == 'GET':             # render the form to edit the user's info
        return render_template('my_info.html', title="My Info", active={'my_info':True})
#    elif request.method == 'POST':          # form is submitted
#        return render_template('display_info.html', title="My Info", active={'display_info':True})

@app.route('/display_info', methods=["GET", "POST"])
def display_info():
    if request.method == 'GET':             # render the user's info
        return render_template('display_info.html', title="My Info", active={'my_info':True})
    elif request.method == 'POST':          # Edit Info form was submitted, get the values and display them
        month = request.form['month']
        day = request.form['day']
        year = request.form['year']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        address = request.form['address']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']
        country = request.form['country']
        days = int(request.form['days'])
        hours = int(request.form['hours'])
        intensity = int(request.form['intensity'])
        miles = int(request.form['miles'])

        # calculate the user's fitness level
        # first get the average number of hours of physical activity per week
        avg_hours = days * hours // 7
        level = avg_hours
        # adjust level based off of the user's intensity when hiking
        if intensity > avg_hours and avg_hours <= 3:
            level += 1
        elif intensity < avg_hours and avg_hours >= 2:
            level -= 1
        # adjust level based off of the user's average length for a hike
        if miles > avg_hours and level <= 3:
            level += 1
        elif miles < avg_hours and level >= 2:
            level -= 1
        # ensure level is a value from 1-4
        if level <= 1:
            level = 1
        # create names for fitness levels
        level_str = ""
        if level == 1:
            level_str = "low"
        elif level == 2:
            level_str = "medium"
        elif level == 3:
            level_str = "high"
        elif level == 4:
            level_str = "very high"

        return render_template('display_info.html', title="My Info", active={'my_info':True}, month=month, day=day, year=year,
        gender=gender, height=height, weight=weight, address=address, address2=address2, city=city, state=state, zip=zip, 
        country=country, level=level_str)

@app.route('/signin', methods=["GET", "POST"])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('display_info'))
    return render_template('signin.html', title="Sign In / Sign Up", active={'signin':True}, form=form)


if __name__ == '__main__':
   app.run(debug=True)