from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.ext.session import Session
from config.main import SECRET_KEY

# Flask Setup
app = Flask(__name__)
app.config['SERVER_NAME'] = 'dev.localhost'
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_DOMAIN'] = 'http://dev.localhost:8080'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///litterbug.db'
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
Session(app)

# Import models
import models.user
db.create_all()

# Attach blueprints
from routes.main import main
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(host='dev.localhost', port=5000)