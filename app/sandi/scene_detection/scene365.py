import os

import numpy as np
import scipy
import skimage
import cv2
import caffe
import pickle
from PIL import Image

from app import app

class SceneDetection:
    """Runs Scene Detection application
    
    Returns:
        None
    """
    DESIGN = os.environ['SCENE_DETECTION_DESIGN']
    WEIGHTS = os.environ['SCENE_DETECTION_WEIGHTS']
    LABELS = os.environ['SCENE_DETECTION_LABELS']
    NPY = os.environ['SCENE_DETECTION_NPY']

    DATA = 'data'
    PROB = 'prob'

    def __init__(self, scene_resources):
        """Initializes resources for scene detection
        
        Args:
            scene_resources (tuple): (neural_network, transformer, labels)
        """
        self.scene_resources = scene_resources

    def run(self, filenames, images_dir):
        """Runs scene detection application

        Runs scene detection application and gathers tags from results
        
        Args:
            filenames (list): list of filenames
            images_dir (str): path of directory where images are stored
        
        Returns:
            dict: {filename: [tag1, tag2, ...]}
        """
        app.logger.info('Starting scene detection analysis')
        
        net, transformer, labels = self.scene_resources
        
        scene_detection_tags = dict()
        
        for filename in filenames:

            image_path = os.path.join(images_dir, filename)

            # im = self.load_image(image_path) 
            im = caffe.io.load_image(image_path)

            # load the image in the data layer
            net.blobs['data'].data[...] = transformer.preprocess('data', im)

            # compute
            out = net.forward()
            
            top_k = net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]

            try:
                scene_detection_tags[filename] = set(labels[top_k[0]].split('_'))

                app.logger.debug('Scene tags {filename}: {results}'.format(filename=filename, results=scene_detection_tags[filename]))
            except Exception:
                pass

        app.logger.info('Finished scene detection analysis')

        return scene_detection_tags

    def load_image(self, image_path):
        """Load in image
        
        Args:
            image_path (str): full path to image
        
        Returns:
            np.array: image as array
        """
        app.logger.info('Loading scene image {image}'.format(image=image_path))

        img = skimage.img_as_float(cv2.imread(image_path)).astype(np.float32)
        if img.ndim == 2:
            img = img[:, :, np.newaxis]
            img = np.tile(img, (1, 1, 3))
        elif img.shape[2] == 4:
            img = img[:, :, :3]
        return img

    @staticmethod
    def load_resources():
        """Loads in resources for scene detection
        
        Returns:
            tuple: (neural_network, transformer, labels)
        """
        app.logger.debug('Loading scene detection nets and transformers')

        # initialize net
        net = caffe.Net(SceneDetection.DESIGN, SceneDetection.WEIGHTS, caffe.TEST)

        # load input and configure preprocessing
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        transformer.set_mean('data', np.load(SceneDetection.NPY).mean(1).mean(1))
        transformer.set_transpose('data', (2,0,1))
        transformer.set_channel_swap('data', (2,1,0))
        transformer.set_raw_scale('data', 255.0)

        # since we classify only one image, we change batch size from 10 to 1
        net.blobs['data'].reshape(1,3,227,227)

        # load in tags
        with open(SceneDetection.LABELS, 'rb') as f:
            labels = pickle.load(f)

        return (net, transformer, labels)