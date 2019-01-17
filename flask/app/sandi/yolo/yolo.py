import os
import lightnet

from app import app

class Yolo:
    """Runs the YoloV2 application

    Returns:
        None
    """
    MODEL  = os.environ['YOLO_MODEL_NAME']
    THRESH = float(os.environ['YOLO_THRESH'])

    def __init__(self, model):
        """Initializes model

        Args:
            model (model): YoloV2 model
        """
        self.model = model

    def run(self, file_names, images_dir):
        """Runs YoloV2 Application

        Runs YoloV2 application and gathers tags from results

        Args:
            file_names (list): list of file names
            images_dir (str): path of directory where images are stored

        Returns:
            dict: {filename: [tag1, tag2, ...]}
        """
        app.logger.info('Starting yolo analysis')

        yolo_tags = dict()

        for file_name in file_names:

            image_path = os.path.join(images_dir, file_name)

            tags = set()

            with open(image_path, 'rb') as image:

                lightnet_image = lightnet.Image.from_bytes(image.read())

                # The thresh parameter controls the prediction threshold.
                # Objects with a detection probability above thresh are returned.
                boxes = self.model(lightnet_image, thresh=Yolo.THRESH)

                [tags.add(box[1]) for box in boxes]

            yolo_tags[file_name] = tags

            app.logger.debug('Yolo tags {file_name}: {results}'.format(file_name=file_name, results=tags))

        app.logger.info('Finished yolo analysis')

        return yolo_tags

    @staticmethod
    def load_resources():
        """Loads in YoloV2 model

        Returns:
            model: YoloV2 model
        """
        app.logger.debug('Loading yolo model')

        return lightnet.load(Yolo.MODEL)