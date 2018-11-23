import os
import lightnet

from app import app

class Yolo:

    YOLO_MODEL = os.environ['YOLO_MODEL_NAME']

    def __init__(self, model):
        self.model = model

    def run(self, images):
        app.logger.info('Starting yolo analysis')

        yolo_tags = dict()

        for filename, image_bytes in images.items():

            lightnet_image = lightnet.Image.from_bytes(image_bytes['data'])
            boxes = self.model(lightnet_image)

            yolo_tags[filename] = set([box[1] for box in boxes])

            app.logger.debug('Analyzed image {filename}: {results}'.format(filename=filename, results=yolo_tags[filename]))

        app.logger.info('Finished yolo analysis')

        return yolo_tags

    @staticmethod
    def load_resources():
        app.logger.debug('Loading yolo model')

        return lightnet.load(Yolo.YOLO_MODEL)