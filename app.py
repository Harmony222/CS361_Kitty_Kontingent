from flask import Flask, render_template, request, redirect, url_for
from gear_functions import get_weather_data, get_trail_data, gear_evaluation
from trail_list_functions import get_trails, list_table
from match_me import filter_trails, filtered_trail_locations, get_map_api_key

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', active={'index':True})

@app.route('/find_trails')
def find_trails():

    # test data, will be filled by user-entered location
    trails_list = get_trails(40.0274, -105.2519, 10)

    # using flask_table to build table for now - see trail_list_functions for more
    trails_table = list_table(trails_list)
    return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails':True},
                            trails_table = trails_table)

@app.route('/map_trail')
def map_trail():
    return render_template('map_trail.html', title='Map Trail', active={'map_trail':True})


@app.route('/match_me')
def match_me():
    trails_list = get_trails(47.60621, -122.3321, 100)
    filtered_trails = filter_trails(trails_list, 1)
    location_list = filtered_trail_locations(filtered_trails)
    map_api_key = get_map_api_key()
    return render_template('match_me.html', title='Match Me With A Trail',
                           active={'match_me': True}, map_api_key=map_api_key,
                           trails_list=trails_list, filtered_trails=filtered_trails,
                           location_list=location_list)


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

@app.route('/my_info')
def my_info():
    if request.method == 'GET':             # render the form to edit the user's info
        return render_template('my_info.html', title="My Info", active={'my_info':True})
    elif request.method == 'POST':          # form is submitted
        month = request.form['month']
        print('What is the month?\n', month)
        day = request.form['day']
        print('What is the day?\n', day)
        year = request.form['year']
        print('What is the year?\n', year)
        address = request.form['address']
        print('What is the address?\n', address)
        address2 = request.form['address2']
        print('What is the address2?\n', address2)
        return render_template('display_info.html', title="My Info", active={'display_info':True})

@app.route('/display_info')
def display_info():
    if request.method == 'GET':             # render the user's info
        return render_template('display_info.html', title="My Info", active={'display_info':True})
    elif request.method == 'POST':          # render the form to edit the user's info
        return render_template('my_info.html', title="My Info", active={'my_info':True})

@app.route('/signin')
def signin():
    return render_template('signin.html', title="Sign In / Sign Up", active={'signin':True})





# if __name__ == '__main__':
#     app.run(debug=True)