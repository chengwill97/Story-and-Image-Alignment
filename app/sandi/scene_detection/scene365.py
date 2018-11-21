import os

import numpy as np
import caffe
import pickle

from app import app

class SceneDetection:

    def __init__(self, scene_net):
        self.scene_net = scene_net

    def run(self, images, folder):
        pass

    @staticmethod
    def load_net():
        return None