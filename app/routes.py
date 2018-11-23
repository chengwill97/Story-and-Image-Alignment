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
    app.logger.info('Setting up server')

    app.logger.debug('Setting up data directory')

    temp_data_path = os.path.abspath(os.environ['TEMP_DATA_PATH'])
    try:
        os.mkdir(temp_data_path)
    except OSError:
        if not os.path.isdir(temp_data_path):
            app.logger.warn('Error creating directory {}'.format(temp_data_path))

    app.logger.debug('Setting up models and nets ')

    global yolo_resources, scene_resources
    yolo_resources  = SandiWorkflow.load_yolo_resources()
    scene_resources = SandiWorkflow.load_scene_resources()
 
    app.logger.info('Server set up')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('homepage.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():

    app.logger.info('Handling Demo Request')

    images = dict()
    paragraphs = list()

    if request.method == 'POST':

        # Initialize workflow for SANDI demo

        demo = SandiWorkflow(yolo_resources=yolo_resources, scene_resources=scene_resources)
        
        # Gather and save images and text files

        demo.collect_uploaded_images(request.files.getlist('images'))

        demo.collect_uploaded_texts(request.files.getlist('texts'))

        # Get tags from yolo and caffe

        demo.run()

        # Order images and text randomly

        results = demo.randomize()

    app.logger.info('Handled Demo Request')

    # return render_template('homepage.html')

    return render_template('demo.html',
                            num_images=len(images),
                            num_texts=len(paragraphs),
                            results=results)

