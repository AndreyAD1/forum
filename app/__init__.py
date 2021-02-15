import logging

from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
if app.config['VERBOSE']:
    app.logger.setLevel(logging.DEBUG)
    database = SQLAlchemy(app, engine_options={'echo': 'debug'})
else:
    database = SQLAlchemy(app)

migrate = Migrate(app, database)

from app import models, user_api, api_auth, api_tokens, post_api
from app import thread_api, forum_api
