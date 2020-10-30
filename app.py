from flask import Flask, render_template, request, redirect
from gear_functions import get_weather_data, get_trail_data, gear_evaluation

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', active={'index':True})

@app.route('/find_trails')
def find_trails():
    return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails':True})

@app.route('/map_trail')
def map_trail():
    return render_template('map_trail.html', title='Map Trail', active={'map_trail':True})

@app.route('/match_me')
def match_me():
    return render_template('match_me.html', title='Match Me With A Trail', active={'match_me':True})

@app.route('/gear', methods=["GET"])
def gear():
    trail_id = 7022927
    trail_data = get_trail_data(trail_id)
    latitude = trail_data["trails"][0]["latitude"]
    longitude = trail_data["trails"][0]["longitude"]
    weather_data = get_weather_data(latitude, longitude)
    gear_data = gear_evaluation(trail_data, weather_data)
    return render_template('gear.html', title='Find Hiking Gear', 
                            active={'gear':True}, weather_data=weather_data,
                            trail_data=trail_data["trails"][0], 
                            gear_data=gear_data)

@app.route('/my_info')
def my_info():
    return render_template('my_info.html', title="My Info", active={'my_info':True})

@app.route('/signin')
def signin():
    return render_template('signin.html', title="Sign In / Sign Up", active={'signin':True})





if __name__ == '__main__':
    app.run(debug=True)