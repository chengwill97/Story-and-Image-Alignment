"""
Dataset loading
"""
import numpy

from app import app

def load_captions(captions_dataset_path):

    app.logger.info('Loading Captions from {}'.format(captions_dataset_path))

    captions = list()

    with open(captions_dataset_path, 'rb') as f:
        captions = [line.strip() for line in f]

    app.logger.info('Finished loading Captions from {}'.format(captions_dataset_path))

    return captions

def load_image_features(image_features_path):

    app.logger.info('Loading image feautres from {}'.format(image_features_path))

    image_features = numpy.load(image_features_path)

    app.logger.info('Finished loading image feautres from {}'.format(image_features_path))

    return image_features