import os

from app import app

from app.sandi.quotes.visual_semantic_embedding import (demo, tools, datasets)

class Quotes:
    """Runs the quote reccomendation application
    
    Returns:
        None
    """
    VSC_RESOURCES       = os.environ['VSC_RESOURCES']
    VSC_DEFAULT_MODEL   = os.environ['VSC_DEFAULT_MODEL']
    VSC_VGG             = os.environ['VSC_VGG']
    VSC_DATASET_NAME    = os.environ['VSC_DATASET_NAME']

    TRAIN   = 0
    DEV     = 1
    TEST    = 2

    CAPTIONS = 0

    def __init__(self, quotes_resources):
        """Initializes resources for quote reccomendation
        
        Args:
            quotes_resources (tuple): (model, neural_network, captions, vectors)
        """
        self.quotes_resources = quotes_resources

    def run(self, filenames, images_dir):
        """Runs Quote suggestion application

        Runs Quote suggestino application and gathers quotes for each image
        
        Args:
            filenames (list): list of filenames
            images_dir (path]): full path to directory of image
        
        Returns:
            [type]: [description]
        """
        app.logger.info('Getting quote reccomendations')

        model, net, captions, vectors = self.quotes_resources

        quote_recs = dict()

        for filename in filenames:
            image = os.path.join(images_dir, filename)
            quotes = demo.retrieve_captions(model, net, captions, vectors, image, k=1)

            try:
                quote_recs[filename] = quotes[0]
                app.logger.debug('Quote {filename}: {results}'.format(filename=filename, results=quote_recs[filename]))
            except IndexError:
                pass

        app.logger.info('Retrieved quote reccomendations')

        return quote_recs

    @staticmethod
    def load_resources():
        """Loads in Quote suggestiion resources
        
        Returns:
            tuple: (model, neural_network, captions, vectors)
        """
        app.logger.debug('Loading quote reccomendation resources')

        net = demo.build_convnet(path_to_vgg=Quotes.VSC_VGG)
        model = tools.load_model(path_to_model=Quotes.VSC_DEFAULT_MODEL)
        captions = datasets.load_dataset(name=Quotes.VSC_DATASET_NAME, path_to_data=Quotes.VSC_RESOURCES)[Quotes.DEV][Quotes.CAPTIONS]
        vectors = tools.encode_sentences(model, captions, verbose=False)

        return (model, net, captions, vectors)