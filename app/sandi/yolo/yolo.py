import os
import lightnet

from app import app

class Yolo:
    """Runs the YoloV2 application

    Returns:
        None
    """
    YOLO_MODEL = os.environ['YOLO_MODEL_NAME']

    def __init__(self, model):
        """Initializes model

        Args:
            model (model): YoloV2 model
        """
        self.model = model

    def run(self, images):
        """Runs YoloV2 Application

        Runs YoloV2 application and gathers tags from results

        Args:
            images (dict): {filename: {'data': byte64, 'conten_type': mime_type}, ...}

        Returns:
            dict: {filename: [tag1, tag2, ...]}
        """
        app.logger.info('Starting yolo analysis')

        yolo_tags = dict()

        for filename, image_bytes in images.items():

            # The thresh parameter controls the prediction threshold.
            # Objects with a detection probability above thresh are returned.
            lightnet_image = lightnet.Image.from_bytes(image_bytes['data'])
            boxes = self.model(lightnet_image, thresh=0.15)

            yolo_tags[filename] = set([box[1] for box in boxes])

            app.logger.debug('Yolo tags {filename}: {results}'.format(filename=filename, results=yolo_tags[filename]))

        app.logger.info('Finished yolo analysis')

        return yolo_tags

    @staticmethod
    def load_resources():
        """Loads in YoloV2 model

        Returns:
            model: YoloV2 model
        """
        app.logger.debug('Loading yolo model')

        return lightnet.load(Yolo.YOLO_MODEL)