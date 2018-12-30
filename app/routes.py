import os
import io
import json
import shutil
import base64
import random
import base64

import cv2
import numpy as np
import pandas as pd
import traceback

from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from flask import request
from flask import session

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
    quote_resources = SandiWorkflow.load_quote_resources()
    glove_resources = SandiWorkflow.load_glove_resources()

    app.logger.info('Server set up')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page of sandi web app

    Returns:
        template: template of home page
    """

    app.logger.info('Starting new session')

    # Reset session
    session.pop('folder', None)
    session.pop('num_images', 0)
    session.pop('num_texts', 0)

    return render_template('homepage.html')

@app.route('/demo/imagesMissingTags')
def images_missing_tags():
    """Requests tags for images without tags

    Returns:
        template: template to get more tags
    """
    try:
        folder = session['folder']
    except:
        return redirect(url_for('index'))

    images_missing_tags = [json.loads(i) for i in request.args.getlist('images_missing_tags')]

    for image_missing_tags in images_missing_tags:
        file_name = image_missing_tags['file_name']
        file_path = os.path.join(folder, SandiWorkflow.IMAGES_FOLDER, file_name)

        with open(file_path, 'r') as image:
            image_missing_tags['data'] = base64.b64encode(image.read()).decode('ascii')

    app.logger.debug('images_missing_tags')

    return render_template('images_missing_tags.html',
                            images_missing_tags=images_missing_tags)

@app.route('/demo', methods=['POST'])
def demo():
    """Page with results of sandi demo

    Returns:
        template: template of demo with results
                  or page to request more tags
    """
    app.logger.info('Handling Demo Request')

    results    = list()
    quotes     = None
    folder     = session.pop('folder', None)
    num_images = session.pop('num_images', 0)
    num_texts  = session.pop('num_texts', 0)

    # Initialize workflow for SANDI demo
    demo = SandiWorkflow(folder=folder,
                         num_images=num_images,
                         num_texts=num_texts,
                         yolo_resources=yolo_resources,
                         scene_resources=scene_resources,
                         quote_resources=quote_resources,
                         glove_resources=glove_resources)

    app.logger.debug('Session contains folder: {folder}'.format(folder=folder))

    if folder == None:

        # Gather and save images and text files
        num_images = demo.collect_uploaded_images(request.files.getlist('images'))
        num_texts  = demo.collect_uploaded_texts(request.files.getlist('texts'))

        # Get tags from yolo and caffe
        images_missing_tags = demo.run_tags()

        if images_missing_tags:
            app.logger.info('Could not retrieve tags for some images')

            session['folder']     = demo.folder
            session['num_images'] = num_images
            session['num_texts']  = num_texts

            return redirect(url_for('images_missing_tags',
                                    images_missing_tags=images_missing_tags))

    else:
        app.logger.info('Gathering tags from user')

        # Get new tags here
        demo.collect_missing_tags(request.form)

    demo.run_alignment()

    if 'include_quotes' in request.form:
        # Get reccomended quotes
        quotes = demo.get_quotes()

    """Get optimized images and texts, and
    if alignment somehow fails, we give
    a randomized order of images and texts
    """
    try:
        # demo.run_alignment()
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