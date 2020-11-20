from app import db
import datetime

# adapted from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    date_of_birth = db.Column(db.Date(), index=True)
    gender = db.Column(db.String(1), index=True)
    height = db.Column(db.Integer(), index=True)
    weight = db.Column(db.Integer(), index=True)
    address = db.Column(db.String(64), index=True)
    address2 = db.Column(db.String(64), index=True)
    fitness_level = db.Column(db.Integer(), index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)