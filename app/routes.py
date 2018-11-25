import os
import io
import shutil
import base64
import random
import cv2
import numpy as np

import lightnet

from flask import (render_template, flash, redirect, url_for, request)

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

    app.logger.debug('Setting up data directory')

    temp_data_path = os.path.abspath(os.environ['TEMP_DATA_PATH'])
    try:
        os.mkdir(temp_data_path)
    except OSError:
        if not os.path.isdir(temp_data_path):
            app.logger.warn('Error creating directory {}'.format(temp_data_path))

    app.logger.debug('Setting up models and nets ')

    global yolo_resources, scene_resources, quote_resources
    yolo_resources  = SandiWorkflow.load_yolo_resources()
    scene_resources = SandiWorkflow.load_scene_resources()
    quote_resources = SandiWorkflow.load_quote_resources()
 
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

    # Initialize workflow for SANDI demo

    demo = SandiWorkflow(yolo_resources=yolo_resources, 
                            scene_resources=scene_resources,
                            quote_resources=quote_resources)

    if request.method == 'POST':
        
        # Gather and save images and text files
        demo.collect_uploaded_images(request.files.getlist('images'))
        demo.collect_uploaded_texts(request.files.getlist('texts'))

        # Get tags from yolo and caffe
        demo.run()

        if 'include_quotes' in request.form:
            # Get reccomended quotes
            quotes = demo.get_quotes()

            # Order images and text randomly
            results = demo.randomize(quotes=quotes)
            
        else :
            results = demo.randomize()
            
    app.logger.info('Handled Demo Request')

    return render_template('demo.html',
                            num_images=len(demo.images_base64),
                            num_texts=len(demo.paragraphs),
                            results=results)