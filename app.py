from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.main import SECRET_KEY

# Flask Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///litterbug.db'
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)

# Import models
import models.user
db.create_all()

# Attach blueprints
from routes.main import main
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(port=5000)