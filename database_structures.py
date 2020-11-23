# import login was also causing circular imports problems, I commented it out here
# because I didn't see it used anywhere in models.py, if its needed we'll have
# to do something else to fix circular imports issue

# from app import login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# imports for forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo

# for database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# adapted from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(1))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    address = db.Column(db.String(64))
    address2 = db.Column(db.String(64))
    fitness_level = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

# adapted from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')