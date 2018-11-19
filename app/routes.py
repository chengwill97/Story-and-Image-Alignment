import os
import io
import shutil
import base64
import random

from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from flask import request

from app import app

from app.sandi.demo import SandiWorkflow

@app.before_first_request
def initServer():
    app.logger.info('Setting up server')

    global model
    model = SandiWorkflow.load_model()

    app.logger.info('Server set up')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('homepage.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():

    app.logger.info('Handling Demo Request')

    images = dict()
    paragraphs = list()
    randomized = list()

    if request.method == 'POST':

        # Collect images
        for input_image in request.files.getlist('images'):
            image_bytes = io.BytesIO(input_image.read()).read()
            image_data = {'data': image_bytes, 'type': input_image.content_type}
            images[input_image.filename] = image_data

        app.logger.info('Collected {num_images} images'.format(num_images=len(images)))

        # Collect paragraphs
        for input_text in request.files.getlist('texts'):
            text = input_text.read().decode('cp1252')
            paragraphs += text.split('\n')

        app.logger.info('Collected {num_texts} paragraphs'.format(num_texts=len(paragraphs)))

        demo = SandiWorkflow(images, paragraphs)

        demo.run_yolo(model)

        results = demo.randomize()

        demo.clean_up()

    app.logger.info('Handled Demo Request')

    return render_template('demo.html',
                            num_images=len(images),
                            num_texts=len(paragraphs),
                            results=results)

