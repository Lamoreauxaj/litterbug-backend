from app import db

class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    picture = db.Column(db.String)
    litterbug = db.Column(db.Integer)