import os
import lightnet

from app import app

class Yolo:

    def __init__(self, model):
        self.model = model

    def run(self, images, folder):
        app.logger.info('Starting yolo analysis')

        app.logger.debug('Saving yolo results to: %s', folder)

        with open(os.path.join(folder, 'yolo_results.txt'), 'w') as f:

            for filename, image in images.items():

                app.logger.debug('Analyzing image {filename}'.format(filename=filename))

                tags = set()
                yolo_result = [filename]
                yolo_image = lightnet.Image.from_bytes(image['data'])
                boxes = self.model(yolo_image)

                # insert class names into results
                for box in boxes:
                    tags.add(box[1])

                yolo_result.append(', '.join(list(tags)) or ',')

                app.logger.debug('Analyzed image {filename} {results}'.format(filename=filename, results=yolo_result[1]))

                f.write('{yolo_result}\n'.format(yolo_result='\t'.join(yolo_result)))

        app.logger.info('Finished yolo analysis')

    @staticmethod
    def load_model():
        app.logger.debug('Loading yolo model')
        return lightnet.load(os.environ['YOLO_MODEL_NAME'])