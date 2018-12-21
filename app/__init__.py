import os
from dotenv import load_dotenv

from flask import Flask

# set environment variables
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

TEMP_DATA_PATH = os.environ['TEMP_DATA_PATH']

app = Flask(__name__)

from app import routes