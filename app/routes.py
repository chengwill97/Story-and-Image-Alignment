import os
import io
import shutil
import base64
import random
import cv2
import base64
import numpy as np
import pandas as pd
import traceback

from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from flask import request

from app import app

from app.sandi.demo import SandiWorkflow

@app.before_first_request
def initServer():
    """Initialize the models and neural nets used for
        Yolo,
        Scene detection,
        and Quote Suggestions
        only before the first request
    """
    app.logger.info('Setting up server')

    temp_data_path = os.path.abspath(os.environ['TEMP_DATA_PATH'])

    app.logger.debug('Setting up data directory {}'.format(temp_data_path))

    try:
        os.mkdir(temp_data_path)
    except OSError:
        if not os.path.isdir(temp_data_path):
            app.logger.warn('Error creating directory {}'.format(temp_data_path))

    app.logger.debug('Setting up models and nets')

    global yolo_resources, scene_resources, quote_resources, glove_resources
    yolo_resources  = SandiWorkflow.load_yolo_resources()
    scene_resources = SandiWorkflow.load_scene_resources()
    quote_resources = None #SandiWorkflow.load_quote_resources()
    glove_resources = None #SandiWorkflow.load_glove_resources()

    app.logger.info('Server set up')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page of sandi web app

    Returns:
        templat: template of home page
    """
    return render_template('homepage.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    """Page with results of sandi demo

    Returns:
        template: template of demo with results
    """
    app.logger.info('Handling Demo Request')

    results    = list()
    quotes     = None
    num_images = 0
    num_texts  = 0

    # Initialize workflow for SANDI demo
    demo = SandiWorkflow(yolo_resources=yolo_resources,
                         scene_resources=scene_resources,
                         quote_resources=quote_resources,
                         glove_resources=glove_resources)

    if request.method == 'POST':

        # Gather and save images and text files
        num_images = demo.collect_uploaded_images(request.files.getlist('images'))
        num_texts  = demo.collect_uploaded_texts(request.files.getlist('texts'))

        # Get tags from yolo and caffe
        demo.run()

        if 'include_quotes' in request.form:
            # Get reccomended quotes
            quotes = demo.get_quotes()

        """Get optimized images and texts, and
        if alignment somehow fails, we give
        a randomized order of images and texts
        """
        try:
            results = demo.get_optimized_alignments(quotes=quotes)
        except Exception as e:
            app.logger.warn(e)
            traceback.print_exc()
            results = demo.get_randomized_alignments(quotes=quotes)

    app.logger.info('Handled Demo Request')

    return render_template('demo.html',
                            num_images=num_images,
                            num_texts=num_texts,
                            results=results)