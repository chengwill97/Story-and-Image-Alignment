import os

import re
from nltk.tokenize.treebank import TreebankWordDetokenizer as Detok

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
        self.detokenizer = Detok()

    def run(self, filenames, k, images_dir):
        """Runs Quote suggestion application

        Runs Quote suggestino application and gathers quotes for each image

        Args:
            filenames (list): list of filenames
            images_dir (path]): full path to directory of image

        Returns:
            dict: {filename: [quote1, quote2, ...], ...}
        """
        app.logger.info('Getting quote reccomendations')

        model, net, captions, vectors = self.quotes_resources

        quote_recs = dict()
        quote_used = dict()

        for filename in filenames:
            image = os.path.join(images_dir, filename)
            quotes = demo.retrieve_captions(model, net, captions,
                                            vectors, image, k=k)

            quote_recs[filename] = [self.detokenize(quote) for quote in quotes]

        app.logger.info('Retrieved quote reccomendations')

        return quote_recs

    def detokenize(self, tokens_str):
        """Detokenizes tokens

        Args:
            tokens_str (str): string of tokens

        Returns:
            str: untokenized string
        """
        detokenized = self.detokenizer.detokenize(tokens_str.split())
        detokenized = re.sub('\s*,\s*', ', ', detokenized)
        detokenized = re.sub('\s*\.\s*', '. ', detokenized)
        detokenized = re.sub('\s*\?\s*', '? ', detokenized)

        return detokenized

    @staticmethod
    def load_resources():
        """Loads in Quote suggestiion resources

        Returns:
            tuple: (model, neural_network, captions, vectors)
        """
        app.logger.debug('Loading quote reccomendation resources')

        net = demo.build_convnet(Quotes.VSC_VGG)
        model = tools.load_model(path_to_model=Quotes.VSC_DEFAULT_MODEL)
        captions = datasets.load_dataset(name=Quotes.VSC_DATASET_NAME, path_to_data=Quotes.VSC_RESOURCES)[Quotes.DEV][Quotes.CAPTIONS]
        vectors = tools.encode_sentences(model, captions, verbose=False)

        return (model, net, captions, vectors)