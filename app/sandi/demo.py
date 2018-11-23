import os
import io
import shutil
import random
import base64

import lightnet

from flask import request

from app import app

from app.sandi.scene_detection.scene365 import SceneDetection
from app.sandi.yolo.yolo                import Yolo
from app.sandi.quotes.quote_rec         import Quotes

class SandiWorkflow:

    TEMP_DATA_PATH  = os.environ['TEMP_DATA_PATH']
    FILENAME_TAGS   = os.environ['FILENAME_TAGS']
    FILENAME_TEXT   = os.environ['FILENAME_TEXT']
    TAGS_DELIM      = os.environ['TAGS_DELIM']

    IMAGES_FOLDER   = 'images'

    def __init__(self, yolo_resources=None, scene_resources=None, quote_resources=None):
        self.images_base64      = dict()
        self.paragraphs         = list()
        self.folder             = None
        self.yolo_resources     = yolo_resources
        self.scene_resources    = scene_resources
        self.quote_resources    = quote_resources
        self.yolo               = Yolo          (self.yolo_resources)
        self.scene              = SceneDetection(self.scene_resources)
        self.quote              = Quotes        (self.quote_resources)

        app.logger.info('Initiating SANDI pipeline')

        # Create directory to store results and images

        self.create_data_folder()

    def run(self):

        app.logger.info('Running SANDI pipeline')
        
        # Obtain tags from the yolo and scene detection models

        yolo_tags = self.yolo.run(self.images_base64)

        scene_detection_tags = self.scene.run(self.images_base64.keys(), os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))

        # Combine then save tags to folder

        app.logger.debug('Combining tags from yolo and scene detection')

        try:
            app.logger.debug('Saving tags to: %s', self.folder)

            with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TAGS), 'w') as f:

                for filename in self.images_base64.keys():

                    union_tags = set()

                    try:
                        union_tags.update(yolo_tags[filename])
                    except KeyError:
                        pass

                    try:
                        union_tags.update(scene_detection_tags[filename])
                    except KeyError:
                        pass

                    f.write('{filename}\t{union_tags}\n'.format(filename=filename,
                                                                union_tags=(SandiWorkflow.TAGS_DELIM.join(union_tags)) or SandiWorkflow.TAGS_DELIM))
        except Exception as e:

            app.logger.exception(e)

        app.logger.info('Finished SANDI pipeline')

    def get_quotes(self):
        
        quotes = self.quote.run(self.images_base64.keys(), os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))

        return quotes

    def collect_uploaded_images(self, uploaded_images):
        
        app.logger.debug('Savings images')

        for upload in uploaded_images:

            upload.save(os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER, upload.filename))

            upload.seek(0)

            upload_bytes = io.BytesIO(upload.read()).read()

            image_data = {'data': upload_bytes, 'type': upload.content_type}

            self.images_base64[upload.filename] = image_data

        app.logger.debug('Collected {num_images} images'.format(num_images=len(uploaded_images)))    

    def collect_uploaded_texts(self, uploaded_texts):

        app.logger.debug('Saving paragraphs')

        self.paragraphs = list()

        for input_text in request.files.getlist('texts'):
            self.paragraphs += input_text.read().decode('cp1252').split('\n')

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TEXT), 'w') as f:
            for index, paragraph in enumerate(self.paragraphs):
                f.write('{index}\t{paragraph}\n'.format(index=index, paragraph=paragraph.encode('utf8')))

        app.logger.debug('Collected {num_texts} paragraphs'.format(num_texts=len(self.paragraphs)))        

    def create_data_folder(self):

        app.logger.debug('Creating data directory')

        self.folder = None
        folder_ind = 0
        while True:
            try:
                self.folder = os.path.join(SandiWorkflow.TEMP_DATA_PATH, str(folder_ind))
                os.mkdir(self.folder)
                os.mkdir(os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))
                break
            except OSError:
                folder_ind += 1
                pass

        app.logger.debug('Data directory created at {dir}'.format(dir=self.folder))

    def clean_up(self):

        app.logger.debug('Erasing data directory')
        
        try:
            shutil.rmtree(self.folder)
        except Exception:
            pass

    def randomize(self, quotes=None):

        app.logger.info('Randomizing images and text')

        randomized = list()
        image_names = list(self.images_base64.keys())

        # sample random numbers
        randomized_ind = random.sample(range(0, len(self.paragraphs)-1), len(self.images_base64))

        cur_ind = 0
        for i in range(len(self.paragraphs)):
            randomized.append(self.paragraphs[i])
            if i in randomized_ind:
                file_name = image_names[cur_ind]
                image_bytes = self.images_base64[file_name]['data']
                image64 = base64.b64encode(image_bytes).decode('ascii')
                
                randomized.append({'file_name': file_name,'data': image64, 'type': self.images_base64[file_name]['type']})

                if quotes:
                    randomized[-1]['quote'] = quotes[file_name]

                    app.logger.debug('Appending quote {quote} to {file_name}'.format(quote=quotes[file_name],file_name=file_name))

                cur_ind += 1

        return randomized

    @staticmethod
    def load_yolo_resources():
        return Yolo.load_resources()

    @staticmethod
    def load_scene_resources():
        return SceneDetection.load_resources()

    @staticmethod
    def load_quote_resources():
        return Quotes.load_resources()