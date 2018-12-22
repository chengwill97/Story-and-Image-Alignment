"""
Dataset loading
"""
import numpy

from os.path import join

#-----------------------------------------------------------------------------#
# Specify dataset(s) location here
#-----------------------------------------------------------------------------#
path_to_data = '/home/willc97/dev/visual_semantic_embedding/'
#-----------------------------------------------------------------------------#

def load_dataset(name='coco', path_to_data='', load_train=False):
    """
    Load captions and image features
    Possible options: f8k, f30k, coco
    """
    loc = join(path_to_data, name)
    
    # Captions
    train_caps, dev_caps, test_caps = [],[],[]
    if load_train:
        with open(join(loc, name+'_train_caps.txt'), 'rb') as f:
            for line in f:
                train_caps.append(line.strip())
    else:
        train_caps = None
    with open(join(loc, name+'_dev_caps.txt'), 'rb') as f:
        for line in f:
            dev_caps.append(line.strip())
    with open(join(loc, name+'_test_caps.txt'), 'rb') as f:
        for line in f:
            test_caps.append(line.strip())
            
    # Image features
    if load_train:
        train_ims = numpy.load(join(loc, name+'_train_ims.npy'))
    else:
        train_ims = None
    dev_ims = numpy.load(join(loc, name+'_dev_ims.npy'))
    test_ims = numpy.load(join(loc, name+'_test_ims.npy'))

    return (train_caps, train_ims), (dev_caps, dev_ims), (test_caps, test_ims)

