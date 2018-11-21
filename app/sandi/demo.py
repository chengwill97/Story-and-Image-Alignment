import os
import shutil
import random
import base64

import lightnet

from app import app

from app.sandi.scene_detection.scene365 import SceneDetection
from app.sandi.yolo.yolo                import Yolo

class SandiWorkflow:

    def __init__(self, images, paragraphs, yolo_model, scene_net):
        self.images = images
        self.paragraphs = paragraphs
        self.yolo_model = yolo_model
        self.scene_net = scene_net
        self.folder = None

        self.yolo = Yolo(yolo_model)
        self.scene = SceneDetection(scene_net)

        app.logger.info('Starting SANDI pipeline')

        self.create_temp_folder()

        app.logger.debug('Saving paragraphs to: %s', self.folder)

        with open(os.path.join(self.folder, 'paragraphs.txt'), 'w') as f:
            for index, paragraph in enumerate(self.paragraphs):
                f.write('{index}\t{paragraph}\n'.format(index=index, paragraph=paragraph.encode('utf8')))

    def run(self):
        self.yolo.run(self.images, self.folder)

        self.scene.run(self.images, self.folder)

    def create_temp_folder(self):
        app.logger.debug('Creating temporary directory')
        self.folder = None
        folder_ind = 0
        while True:
            try:
                self.folder = os.path.join(os.environ['TEMP_DATA_PATH'], str(folder_ind))
                os.mkdir(self.folder)
                break
            except OSError:
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

    @staticmethod
    def load_yolo_model():
        return Yolo.load_model()

    @staticmethod
    def load_scene_net():
        return SceneDetection.load_net()