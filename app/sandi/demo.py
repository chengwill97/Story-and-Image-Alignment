import os
import io
import shutil
import random
import base64
import requests

import lightnet

from flask import request

from app import app

# from app.sandi.scene_detection.scene365 import SceneDetection
from app.sandi.yolo.yolo                import Yolo
from app.sandi.quotes.quote_rec         import Quotes

class SandiWorkflow:
    """Runs the YOLOV2, Scene Detection,
        and Quote Suggestion applications

    Returns:
        None
    """
    SANDI_ALIGNMENT_URI  = os.environ['SANDI_ALIGNMENT_URI']
    TEMP_DATA_PATH       = os.environ['TEMP_DATA_PATH']
    FILENAME_TAGS        = os.environ['FILENAME_TAGS']
    FILENAME_TEXT        = os.environ['FILENAME_TEXT']
    FILENAME_ALIGN       = os.environ['FILENAME_ALIGN']
    TAGS_DELIM           = os.environ['TAGS_DELIM']
    IMAGES_FOLDER        = 'images'

    def __init__(self, yolo_resources=None, scene_resources=None, quote_resources=None):
        """Initialization

        Initializes the models and neural nets.
        Creates the transient data directories
        that stores results and images.

        yolo_resources (model, optional): Defaults to None.
            YoloV2 model
        scene_resources (tuple, optional): Defaults to None.
            (neural_net, transformer, labels)
        quote_resources (tuple, optional): Defaults to None.
            (model, neural_net, captions, vectors)
        """
        self.images_base64      = dict()
        self.paragraphs         = list()
        self.alignments         = dict()
        self.folder             = None
        self.yolo_resources     = yolo_resources
        self.scene_resources    = scene_resources
        self.quote_resources    = quote_resources
        self.yolo               = Yolo          (self.yolo_resources)
        # self.scene              = SceneDetection(self.scene_resources)
        self.quote              = Quotes        (self.quote_resources)

        app.logger.info('Initiating SANDI pipeline')

        # Create directory to store results and images

        self.create_data_folder()

    def run(self):
        """Get tags from images and runs the sandi
        image alignment server application
        """
        self.run_tags()
        self.run_alignment()

    def run_tags(self):
        """Runs the Yolo and Scene detection applications
        and saves the results to run image to text optimization
        """
        app.logger.info('Running SANDI pipeline')

        # Obtain tags from the yolo and scene detection models

        yolo_tags = self.yolo.run(self.images_base64)

        # scene_detection_tags = self.scene.run(self.images_base64.keys(), os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))

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

                    # try:
                    #     union_tags.update(scene_detection_tags[filename])
                    # except KeyError:
                    #     pass

                    f.write('{filename}\t{union_tags}\n'.format(filename=filename,
                                                                union_tags=(SandiWorkflow.TAGS_DELIM.join(union_tags)) or SandiWorkflow.TAGS_DELIM))
        except Exception as e:

            app.logger.exception(e)

        app.logger.info('Finished SANDI pipeline')

    def run_alignment(self):
        """Runs sandi image and text alignment
        application
        """

        # params = {'work_dir': self.folder, 'num_images': len(self.images_base64)}

        # try:
        #     response     = requests.get(url=SandiWorkflow.SANDI_ALIGNMENT_URI, params=params)
        #     data         = response.json()
        #     self.aligned = data['aligned']
        # except Exception as e:
        #     app.logger.exception(e)

        pre_commands = 'export GUROBI_HOME="/home/willc97/dev/python2.7/gurobi810/linux64"; \
                        export PATH="${PATH}:${GUROBI_HOME}/bin"; \
                        export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"; \
                        export GRB_LICENSE_FILE="${GUROBI_HOME}/gurobi.lic"; '

        command = '{pre_commands} {command} {flags} {jar} \
                    {data_folder} {num_images} {model_folder}'.format(
                        pre_commands='',
                        command='java',
                        flags='-jar',
                        jar='/home/willc97/dev/python2.7/SANDI/SANDI_main.jar',
                        data_folder=os.path.abspath(self.folder),
                        num_images=min(len(self.images_base64), len(self.paragraphs)),
                        model_folder='/home/willc97/dev/python2.7/SANDI/')
        app.logger.debug('Executing: \n {command}'.format(command=command))
        os.system(command)

    def get_alignment(self, quotes=None):
        """Get alignment from '{folder}/alignments.txt'

        Raises:
            Exception: '{folder}/alignments.txt' does not exist

        Returns:
            dict: maps paragraph number to image name
                e.g. {para_id, filename, ...}
        """
        """Get alignment from '{folder}/alignments.txt'
        """

        if not os.path.exists(os.path.join(self.folder, SandiWorkflow.FILENAME_ALIGN)):
            raise Exception('file "{path}" does not exist'.format(path=os.path.join(self.folder, 'alignment.txt')))

        """
        TODO: read from alignments from alignment.txt
        """

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_ALIGN)) as f:
            for line in f:
                align = line.split('\n')[0].split('\t')
                self.alignments[int(align[0])] = align[1]

        image_names = list(self.images_base64.keys())
        results = list()

        for i in range(len(self.paragraphs)):
            results.append(self.paragraphs[i])

            if i in self.alignments:
                file_name   = self.alignments[i]
                image_bytes = self.images_base64[file_name]['data']
                image64     = base64.b64encode(image_bytes).decode('ascii')

                results.append({'file_name': file_name,
                                'data': image64,
                                'type': self.images_base64[file_name]['type']})

                if quotes:
                    results[-1]['quote'] = quotes[file_name]

                    app.logger.debug('Appending quote {quote} to {file_name}'.format(quote=quotes[file_name],file_name=file_name))

        return results

    def get_quotes(self):
        """Runs quote suggestion applicaiton

        Returns:
            dict: {filename: quote, ...}
        """
        quotes = self.quote.run(self.images_base64.keys(), os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))

        return quotes

    def collect_uploaded_images(self, uploaded_images):
        """Save images from user to local filesystem

        Args:
            uploaded_images (list): list of flask image objects
        """
        app.logger.debug('Savings images')

        for upload in uploaded_images:

            upload.save(os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER, upload.filename))

            upload.seek(0)

            upload_bytes = io.BytesIO(upload.read()).read()

            image_data = {'data': upload_bytes, 'type': upload.content_type}

            self.images_base64[upload.filename] = image_data

        app.logger.debug('Collected {num_images} images'.format(num_images=len(uploaded_images)))

    def collect_uploaded_texts(self, uploaded_texts):
        """Save texts from user to local filesystem

        Args:
            uploaded_texts (list): list of flask text files
        """
        app.logger.debug('Saving paragraphs')

        self.paragraphs = list()

        for input_text in request.files.getlist('texts'):
            self.paragraphs += input_text.read().decode('cp1252').split('\n')

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TEXT), 'w') as f:
            for index, paragraph in enumerate(self.paragraphs):
                f.write('{index}\t{paragraph}\n'.format(index=index+1, paragraph=paragraph.encode('utf8')))

        app.logger.debug('Collected {num_texts} paragraphs'.format(num_texts=len(self.paragraphs)))

    def create_data_folder(self):
        """Create transient folder to store images, text, and results
        """
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
        """Remove transient folder
        """
        app.logger.debug('Erasing data directory')

        try:
            shutil.rmtree(self.folder)
        except Exception:
            pass

    def randomize(self, quotes=None):
        """Randomly assigns at most one image to one paragraph
            quotes (dict, optional): Defaults to None. {filename: quote, ...}

        Returns:
            list: elements are either text or images with quotes if given
        """
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
        """Loads in YoloV2 model

        Returns:
            model: YoloV2 model
        """
        return Yolo.load_resources()

    @staticmethod
    def load_scene_resources():
        """Loads in resourecs needed for scene detection

        Returns:
            tuple: (neural_network, transformer, labels)
        """
        # return SceneDetection.load_resources()
        return None

    @staticmethod
    def load_quote_resources():
        """Loads in resources needed for quote suggestions

        Returns:
            tuple: (model, neural_network, captions, vectors)
        """
        return Quotes.load_resources()