import os
import logging

from dotenv import load_dotenv

from flask import Flask

app = Flask(__name__)

env = os.environ.get('FLASK_ENV', 'Development')

log_level = os.environ.get('LOG_LEVEL', logging.DEBUG)

app.logger.setLevel(int(log_level))

try:

    app.config.from_object('app.config.{env}'.format(env=env))

except ImportError:

    app.logger.warn('Environment {env} not found'.format(env=env))
    app.logger.warn('Defaulting to Development environment')

    app.config.from_object('app.config.{default_env}'.format(default_env='Development'))

except Exception as e:

    app.logger.warn('Environment {env} not found'.format(env=env))
    app.logger.warn(e)

from app import routes