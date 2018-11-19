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

TEMP_DATA_PATH = os.environ['TEMP_DATA_PATH']

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

        # Create new folder to store images
        folder = None
        folder_ind = 0
        while True:
            try:
                folder = os.path.join(TEMP_DATA_PATH, str(folder_ind))
                os.mkdir(folder)
                break
            except Exception:
                folder_ind += 1
                pass

        # Collect images
        for input_image in request.files.getlist('images'):
            image_bytes = io.BytesIO(input_image.read())
            image_encoded = base64.b64encode(image_bytes.read()).decode('ascii')

            image_data = {'data': image_encoded, 'type': input_image.content_type}
            images[input_image.filename] = image_data

        app.logger.info('Collected {num_images} images'.format(num_images=len(images)))

        # Collect paragraphs
        for input_text in request.files.getlist('texts'):
            text = input_text.read().decode('cp1252')
            paragraphs += text.split('\n')

        app.logger.info('Collected {num_texts} paragraphs'.format(num_texts=len(paragraphs)))

        app.logger.info('Randoming images and text')

        image_names = list(images.keys())
        randomized_ind = random.sample(range(0, len(paragraphs)-1), len(images))

        cur_ind = 0
        for i in range(len(paragraphs)):
            randomized.append(paragraphs[i])
            if i in randomized_ind:
                randomized.append(images[image_names[cur_ind]])
                cur_ind += 1

        # Remove directory
        try:
            shutil.rmtree(folder)
        except Exception:
            pass

    app.logger.info('Handled Demo Request')

    return render_template('demo.html',
                            num_images=len(images),
                            num_texts=len(paragraphs),
                            randomized=randomized)

