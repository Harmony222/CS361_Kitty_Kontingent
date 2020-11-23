from flask import Flask, render_template, request, redirect, url_for, flash
from gear_functions import get_weather_data, get_trail_data, gear_evaluation
from trail_list_functions import get_trails, get_custom_trails
from match_me import filter_trails, trail_locations, calculate_fitness #,get_map_api_key
from map_trail import get_lat_long, get_string
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user
from database_structures import *
from config import Config, map_api_key
import datetime, calendar
# from extensions import db
# from forms import LoginForm, RegistrationForm
# import webbrowser, datetime, calendar
# from flask_sqlalchemy import SQLAlchemy

# TODO: PRIORITY - FIX ERROR FROM INVALID ADDRESS ENTERED
# TODO: when "filter trails just for me" is used, it does not save the custom filter options 
# (eg. length, difficulty) selected before - create variables to pass these back and forth from app.py and html
# TODO: save "radius" and "address" if navigated to from "find trails" page to "fitness values" page 
# (and back again)
# TODO: auto-populate drop-down selections for user on "fitness values" page if they had previously made slections
# (and then the page was re-loaded or navigated away from)
# TODO: save trail list results between pages?
# TODO: check if user is logged in before allowing 'edit info'
# TODO: change lat/long printed on trails list page to adress string
# TODO: add "distance to trail" column? (suggested by client)

## TRAIL LIST STRUCTURE RETURNED BY GET_TRAILS(LAT, LONG, RAD) - BY INDEX REFERENCE
## 0-id, 1-name, 2-length, 3-difficulty, 4-starVotes, 5-location, 6-url, 7-imgMedium 
## 8-high, 9-low, 10-latitude, 11-longitude, 12-summary, 13-directions_url, 14-gear_url

# Fix circular imports issue
# https://stackoverflow.com/questions/42909816/can-i-avoid-circular-imports-in-flask-and-sqlalchemy
def register_extensions(app):
    db.init_app(app)

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    return app

app = create_app(Config)
# app = Flask(__name__)
# app.config.from_object(Config)
# db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

@app.route('/')
def index():
    return render_template('index.html', active={'index':True})


@app.route('/find_trails', methods= ['GET', 'POST'])
def find_trails():
    '''find trails page to display table with trail data'''
    # convert difficulty string into difficulty level
    diff_dict = { "green": 0, "greenBlue": 1, "blue": 2, "blueBlack": 3, "black": 4, "dblack": 5}

    # check for logged in user and get fitness if it exists
    if current_user.is_authenticated:
        curr_user = db.session.query(User).filter_by(username=current_user.username).first()
        if curr_user.fitness_level is not None:
            user_fitness = curr_user.fitness_level
        else:
            user_fitness = False

    # if user has entered trail search location data
    if request.method == 'POST' and request.form['rad'] != 'False':
        rad, addr = request.form['rad'], request.form['address']
        lat, long = get_lat_long(addr)   

        # change addr to single string for jinja reference, check if valid
        if lat:    
            new_addr = get_string(lat, long)
        else:
            return redirect(url_for('find_trails')) 
        # get unfiltered trails list
        all_trails_list = get_trails(lat, long, rad)

        # Get optional search values and create new, custom list if any values are not None
        min_length = request.form.get('min_length') or 0
        max_length = request.form.get('max_length') or False
        difficulty = request.form.get('difficulty') or False
        if difficulty or (float(min_length) > 0) or max_length:
            all_trails_list = get_custom_trails(all_trails_list, min_length, max_length, difficulty)
        
        locations = trail_locations(all_trails_list)
        active_tab = 'list'
        if "active-tab" in request.form:
            active_tab = request.form['active-tab']
        
        # fix string to bool, don't overwrite logged-in user
        if request.form['user_fitness'] == 'False':
            if not current_user.is_authenticated:
                user_fitness = False
        else:
            user_fitness = int(request.form['user_fitness'])

        # check for no results
        no_results=False
        if len(all_trails_list) == 0:
            no_results=True
        
        # check for filter or a cleared filter for original list
        if "filter-slider" not in request.form or "clear" in request.form:
            return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails': True},
                                   trails_list=all_trails_list, radius=rad, address=addr, filtered=False,
                                   map_api_key=map_api_key, lat=lat, lon=long, locations=locations, 
                                   view_tab=active_tab, user_fitness=user_fitness, diff_dict=diff_dict,
                                   new_addr=new_addr, no_results=no_results)

        # filter trails
        else:
            # check for fitness value
            user_fitness = request.form['user_fitness']
            # filter trails on slider value
            trails_list = filter_trails(all_trails_list, request.form["filter-slider"], user_fitness)
            locations = trail_locations(trails_list)
            if len(trails_list) == 0:
                no_results=True
            return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails': True},
                                       trails_list=trails_list, radius=rad, address=addr, filtered=True,
                                       map_api_key=map_api_key, lat=lat, lon=long, locations=locations,
                                       view_tab=active_tab, user_fitness=user_fitness, diff_dict=diff_dict,
                                       new_addr=new_addr, no_results=no_results)
    # else render page asking for data
    else:
        # check for logged-in user
        if not current_user.is_authenticated:
            # fix strings from forms
            if 'user_fitness' in request.form:
                if request.form['user_fitness'] == 'False':
                    user_fitness = False
                else:
                    user_fitness = int(request.form['user_fitness'])
            else:
                user_fitness = False

        return render_template('find_trails_get.html', title='Find Hiking Trails', active={'find_trails': True}, 
                                user_fitness=user_fitness)

@app.route('/gear', methods=["GET"])
def gear():
    if request.method == "GET" and request.args:
        trail_id = request.args["trail_id"]
    else:
        trail_id = None
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

@app.route('/fitness_values', methods=["GET", "POST"])
def fitness_values():
    # redirect to info page if logged in
    if current_user.is_authenticated:
        return redirect(url_for('display_info'))

    # checks for data received by page
    user_fitness = request.form.get('user_fitness') or False
    radius = request.form.get('rad') or False
    address = request.form.get('address') or False
    incomplete = False

    # directed to self after form filled, check if all values present
    if 'days' in request.form or 'hours' in request.form or 'miles' in request.form or 'intensity' in request.form:
        if 'days' in request.form and 'hours' in request.form and 'miles' in request.form and 'intensity' in request.form:
            user_fitness = calculate_fitness(request.form['days'], request.form['hours'], request.form['miles'], request.form['intensity'])
        else:
            incomplete = True

    # fix incomplete address being passed between pages
    if address and address != 'False':
        lat, long = get_lat_long(address)
        if lat:    
            address = get_string(lat, long)

    return render_template('fitness_values.html', title="Fitness Calculation", active={'fitness_values':True},
                            user_fitness=user_fitness, radius=radius, address=address, incomplete=incomplete)

@app.route('/my_info', methods=["GET"])
def my_info():
    if request.method == 'GET':
        return render_template('my_info.html', title="My Info", active={'my_info':True})
    elif request.method == 'POST':
       return render_template('display_info.html', title="My Info", active={'display_info':True})

@app.route('/display_info', methods=["GET", "POST"])
def display_info():
    if request.method == 'GET':             # render the user's info
        if current_user.is_authenticated:
            curr_user = db.session.query(User).filter_by(username=current_user.username).first()
            if curr_user.date_of_birth is not None:
                year = curr_user.date_of_birth.year
                month = calendar.month_name[curr_user.date_of_birth.month]
                day = curr_user.date_of_birth.day
            else:
                year = ""
                month = ""
                day = ""
            if curr_user.gender == "m":
                gender = "Male"
            elif curr_user.gender == "f":
                gender = "Female"
            else:
                gender = ""

            if curr_user.height is not None:
                total_inches = curr_user.height
                feet = total_inches // 12
                inches = total_inches % 12
                height = str(feet) + "\' " + str(inches) + "\""
            else:
                height = ""
            if curr_user.weight is not None:
                weight = str(curr_user.weight)
            else:
                weight = ""
            if curr_user.address is not None:
                address = curr_user.address
            else:
                address = ""
            if curr_user.address2 is not None:
                address2 = curr_user.address2
            else:
                address2 = ""

            # create names for fitness levels
            level = curr_user.fitness_level
            user_fitness = ""
            if level == 1:
                user_fitness = "low"
            elif level == 2:
                user_fitness = "medium"
            elif level == 3:
                user_fitness = "high"
            elif level == 4:
                user_fitness = "very high"

            return render_template('display_info.html', title="My Info", active={'my_info':True}, username=curr_user.username, 
                                    month=month, day=day, year=year, gender=gender, height=height, weight=weight, 
                                    address=address, address2=address2, user_fitness=user_fitness)
        return render_template('display_info.html', title="My Info", active={'my_info':True})
    elif request.method == 'POST':          # Edit Info form was submitted, get the values and display them
        if current_user.is_authenticated:
            curr_user = db.session.query(User).filter_by(username=current_user.username).first()

            # add form fields to the database for the current user
            month = request.form.get('month') or None
            day = request.form.get('day') or None
            year = request.form.get('year') or None
            if month is not None and day is not None and year is not None:
                birth_date = datetime.date(int(year), int(month), int(day))
                curr_user.date_of_birth = birth_date
            gender = request.form.get('gender') or ""
            if gender == "Male":
                curr_user.gender = "m"
            elif gender == "Female":
                curr_user.gender = "f"
            else:
                curr_user.gender = ""
            if request.form.get('height'):
                curr_user.height = int(request.form.get('height'))
            else:
                curr_user.height = None
            if request.form.get('weight'):
                curr_user.weight = int(request.form.get('weight'))
            else:
                curr_user.weight = None
            curr_user.address = request.form.get('address') or ""
            curr_user.address2 = request.form.get('address2') or ""

    #        city = request.form.get('city') or ""
    #        state = request.form.get('state') or ""
    #        zip_code = request.form.get('zip') or ""
    #        country = request.form.get('country') or ""
            days = int(request.form['days'])
            hours = int(request.form['hours'])
            intensity = int(request.form['intensity'])
            miles = int(request.form['miles'])

            level = calculate_fitness(request.form['days'], request.form['hours'], request.form['miles'], request.form['intensity'])
            curr_user.fitness_level = level
            db.session.commit()

        return redirect(url_for('display_info'))

@app.route('/signin', methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('display_info'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('signin'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('display_info'))
    return render_template('signin.html', title="Sign In / Sign Up", active={'signin':True}, form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('display_info'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('signin'))
    return render_template('signup.html', title="Sign In / Sign Up", active={'signin':True}, form=form)

@app.route('/signout')
def signout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
   app.run(debug=True)