from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
database = SQLAlchemy(app, engine_options={'echo': 'debug'})
migrate = Migrate(app, database)

from app import routes, models, user_api, api_auth, api_tokens
