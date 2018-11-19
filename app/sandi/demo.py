import os
import shutil
import random
import base64

import lightnet

from app import app

class SandiWorkflow:

    def __init__(self, images, paragraphs):
        self.images = images
        self.paragraphs = paragraphs
        self.folder = None

        app.logger.info('Starting SANDI pipeline')

        self.create_temp_folder()

        app.logger.debug('Saving paragraphs to: %s', self.folder)

        with open(os.path.join(self.folder, 'paragraphs.txt'), 'w') as f:
            for paragraph in self.paragraphs:
                f.write('{paragraph}\n'.format(paragraph=paragraph))

    def run_yolo(self, model):
        app.logger.info('Starting yolo analysis')

        app.logger.debug('Saving yolo results to: %s', self.folder)

        with open(os.path.join(self.folder, 'yolo_results.txt'), 'w') as f:

            for filename, image in self.images.items():

                app.logger.debug('Analyzing image {filename}'.format(filename=filename))

                tags = set()
                yolo_result = [filename]
                yolo_image = lightnet.Image.from_bytes(image['data'])
                boxes = model(yolo_image)

                # insert class names into results
                for box in boxes:
                    tags.add(box[1])

                yolo_result.append(','.join(list(tags)) or ',')

                app.logger.debug('Analyzed image {filename} {results}'.format(filename=filename, results=yolo_result[1]))

                f.write('{yolo_result}\n'.format(yolo_result='\t'.join(yolo_result)))

        app.logger.info('Finished yolo analysis')

    def randomize(self):

        app.logger.info('Randomizing images and text')

        randomized = list()
        image_names = list(self.images.keys())

        # sample random numbers
        randomized_ind = random.sample(range(0, len(self.paragraphs)-1), len(self.images))

        cur_ind = 0
        for i in range(len(self.paragraphs)):
            randomized.append(self.paragraphs[i])
            if i in randomized_ind:
                file_name = image_names[cur_ind]
                image64 = base64.b64encode(self.images[file_name]['data']).decode('ascii')
                randomized.append({'data': image64, 'type': self.images[file_name]['type']})
                cur_ind += 1

        return randomized

    def create_temp_folder(self):
        app.logger.debug('Creating temporary directory')
        self.folder = None
        folder_ind = 0
        while True:
            try:
                self.folder = os.path.join(os.environ['TEMP_DATA_PATH'], str(folder_ind))
                os.mkdir(self.folder)
                break
            except Exception:
                folder_ind += 1
                pass

        app.logger.debug('Temporary directory created')

    def remove_temp_folder(self):
        try:
            shutil.rmtree(self.folder)
        except Exception:
            pass

    def clean_up(self):
        self.remove_temp_folder()

    @staticmethod
    def load_model():
        app.logger.debug('Loading model')
        return lightnet.load(os.environ['MODEL_NAME'])