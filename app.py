from flask import Flask, render_template, request, redirect
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

@app.route('/gear')
def gear():
    return render_template('gear.html', title='Find Hiking Gear', active={'gear':True})

@app.route('/my_info')
def my_info():
    return render_template('my_info.html', title="My Info", active={'my_info':True})

@app.route('/signin')
def signin():
    return render_template('signin.html', title="Sign In / Sign Up", active={'signin':True})





if __name__ == '__main__':
    app.run(debug=True)