from flask import Flask, render_template, request, redirect, url_for, flash
from gear_functions import get_weather_data, get_trail_data, gear_evaluation
from trail_list_functions import get_trails, get_custom_trails
from match_me import filter_trails, trail_locations, get_map_api_key, calculate_fitness
from map_trail import get_lat_long, get_string
# from forms import LoginForm, RegistrationForm
import webbrowser
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user
from models import *
import datetime
import calendar

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

# TODO: save "radius" and "address" if navigated to from "find trails" page to "fitness values" page 
# (and back again)
# TODO: auto-populate drop-down selections for user on "fitness values" page if they had previously made slections
# (and then the page was re-loaded or navigated away from)
# TODO: save trail list results between pages?

## TRAIL LIST STRUCTURE RETURNED BY GET_TRAILS(LAT, LONG, RAD) - BY INDEX REFERENCE
## 0-id, 1-name, 2-length, 3-difficulty, 4-starVotes, 5-location, 6-url, 7-imgMedium 
## 8-high, 9-low, 10-latitude, 11-longitude, 12-summary, 13-directions_url, 14-gear_url

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

    # check for logged in user and get fitness
    if current_user.is_authenticated:
        curr_user = db.session.query(User).filter_by(username=current_user.username).first()
        user_fitness = curr_user.fitness_level

    # if user has entered trail search location data
    if request.method == 'POST' and request.form['rad'] != 'False':
        map_api_key = get_map_api_key()
        rad, addr = request.form['rad'], request.form['address']
        lat, long = get_lat_long(addr)    
        all_trails_list = get_trails(lat, long, rad)

        # change addr to single string for jinja reference
        new_addr = get_string(lat, long)

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
        
        if request.form['user_fitness'] == 'False' and not isinstance(user_fitness, int):
            user_fitness = False
        else:
            user_fitness = int(request.form['user_fitness'])
        
        # check for filter or a cleared filter for original list
        if "filter-slider" not in request.form or "clear" in request.form:
            return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails': True},
                                   trails_list=all_trails_list, radius=rad, address=addr, filtered=False,
                                   map_api_key=map_api_key, lat=lat, lon=long, locations=locations, 
                                   view_tab=active_tab, user_fitness=user_fitness, diff_dict=diff_dict,
                                   new_addr=new_addr)

        # filter trails
        else:
            # check for fitness value
            user_fitness = request.form['user_fitness']
            # filter trails on slider value
            trails_list = filter_trails(all_trails_list, request.form["filter-slider"], user_fitness)
            locations = trail_locations(trails_list)
            return render_template('find_trails.html', title='Find Hiking Trails', active={'find_trails': True},
                                       trails_list=trails_list, radius=rad, address=addr, filtered=True,
                                       map_api_key=map_api_key, lat=lat, lon=long, locations=locations,
                                       view_tab=active_tab, user_fitness=user_fitness, diff_dict=diff_dict,
                                       new_addr=new_addr)
    # else render page asking for data
    else:
        # save fitness calculation
        if not isinstance(user_fitness, int):
            user_fitness = False
        if request.method == 'POST':
            user_fitness = calculate_fitness(request.form['days'], request.form['hours'], request.form['miles'], request.form['intensity'])
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
    user_fitness = radius = address = False
    if request.method == 'POST':
        user_fitness = calculate_fitness(request.form['days'], request.form['hours'], request.form['miles'], request.form['intensity'])
    if 'rad' in request.form and request.form['rad'] != 'False':
        radius, address = request.form['rad'], request.form['address']
    return render_template('fitness_values.html', title="Fitness Calculation", active={'fitness_values':True},
                            user_fitness=user_fitness, radius=radius, address=address)

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
            month = int(request.form.get('month')) or None
            day = int(request.form.get('day')) or None
            year = int(request.form.get('year')) or None
            if month is not None and day is not None and year is not None:
                birth_date = datetime.date(year, month, day)
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