import os
import logging
from dotenv import load_dotenv

# load environment variables
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

class Config:
    DEBUG = False
    TESTING = False

    LOG_LEVEL = os.environ.get('LOG_LEVEL') or logging.DEBUG

    APP_DIR = os.environ.get('APP_DIR')

    TEMP_DATA_PATH = os.environ.get('TEMP_DATA_PATH')

    EXAMPLES_PATH = os.environ.get('EXAMPLES_PATH')

    SANDI_ALIGNMENT_URI = None

    SECRET_KEY = os.environ.get('SECRET_KEY')

    FILENAME_TAGS = os.environ.get('FILENAME_TAGS')
    FILENAME_TEXT = os.environ.get('FILENAME_TEXT')
    FILENAME_ALIGN = os.environ.get('FILENAME_ALIGN')
    TAGS_DELIM = os.environ.get('TAGS_DELIM')
    IMAGES_FOLDER = os.environ.get('IMAGES_FOLDER')

    YOLO_MODEL_NAME = os.environ.get('YOLO_MODEL_NAME')
    YOLO_THRESH = os.environ.get('YOLO_THRESH')

    SCENE_DETECTION_RESOURCES = os.environ.get('SCENE_DETECTION_RESOURCES')
    SCENE_DETECTION_DESIGN = os.environ.get('SCENE_DETECTION_DESIGN')
    SCENE_DETECTION_WEIGHTS = os.environ.get('SCENE_DETECTION_WEIGHTS')
    SCENE_DETECTION_LABELS = os.environ.get('SCENE_DETECTION_LABELS')
    SCENE_DETECTION_NPY = os.environ.get('SCENE_DETECTION_NPY')

    VSC_RESOURCES = os.environ.get('VSC_RESOURCES')
    VSC_CAPTIONS = None
    VSC_MODEL = os.environ.get('VSC_MODEL')
    VSC_VGG = os.environ.get('VSC_VGG')
    VSC_DICTIONARY = os.environ.get('VSC_DICTIONARY')
    VSC_MODEL_OPTIONS = os.environ.get('VSC_MODEL_OPTIONS')

    GLOVE_RESOURCES = os.environ.get('GLOVE_RESOURCES')
    DIMENSION = os.environ.get('DIMENSION')
    GLOVE_DEFAULT_MODEL = os.environ.get('GLOVE_DEFAULT_MODEL')

    SEARCH_BY_IMAGE_URL = os.environ.get('SEARCH_BY_IMAGE_URL')
    USER_AGENT = os.environ.get('USER_AGENT')

class Production(Config):
    VSC_CAPTIONS = os.environ.get('VSC_CAPTIONS_PROD')
    SANDI_ALIGNMENT_URI = os.environ.get('SANDI_ALIGNMENT_URI_PROD')

class Testing(Config):
    TESTING = True

    VSC_CAPTIONS = os.environ.get('VSC_CAPTIONS_DEV')
    SANDI_ALIGNMENT_URI = os.environ.get('SANDI_ALIGNMENT_URI_DEV')

class Development(Config):
    DEBUG = True

    VSC_CAPTIONS = os.environ.get('VSC_CAPTIONS_DEV')
    SANDI_ALIGNMENT_URI = os.environ.get('SANDI_ALIGNMENT_URI_DEV')