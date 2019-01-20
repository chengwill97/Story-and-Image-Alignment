import os
import io
import json
import shutil
import random
import base64
import requests

from multiprocessing.pool import ThreadPool

from magic import Magic
import lightnet

from flask import request

from app import app

# from app.sandi.scene_detection.scene365 import SceneDetection
from app.sandi.yolo.yolo                import Yolo
from app.sandi.quotes.quote_rec         import Quotes
from app.sandi.glove.glove              import GloveVectors
from app.sandi.google.images            import ImageSearch

class SandiWorkflow:
    """Runs the YOLOV2, Scene Detection,
        and Quote Suggestion applications

    Returns:
        None
    """
    SANDI_ALIGNMENT_URI  = os.environ['SANDI_ALIGNMENT_URI']
    TEMP_DATA_PATH       = os.environ['TEMP_DATA_PATH']
    FILENAME_TAGS        = os.environ['FILENAME_TAGS']
    FILENAME_TEXT        = os.environ['FILENAME_TEXT']
    FILENAME_ALIGN       = os.environ['FILENAME_ALIGN']
    TAGS_DELIM           = os.environ['TAGS_DELIM']
    IMAGES_FOLDER        = os.environ['IMAGES_FOLDER']

    def __init__(self, folder=None, num_images=0, num_texts=0,
                 yolo_resources=None, scene_resources=None, quote_resources=None,
                 glove_resources=None):
        """Initialization

        Initializes the models and neural nets.
        Creates the transient data directories
        that stores results and images.

        yolo_resources (model, optional): Defaults to None.
            YoloV2 model
        scene_resources (tuple, optional): Defaults to None.
            (neural_net, transformer, labels)
        quote_resources (tuple, optional): Defaults to None.
            (model, neural_net, captions, vectors)
        """
        self.folder             = folder
        self.alignments         = dict()
        self.image_names        = list()
        self.num_images         = num_images
        self.num_texts          = num_texts
        self.yolo_resources     = yolo_resources
        self.scene_resources    = scene_resources
        self.quote_resources    = quote_resources
        self.glove_resources    = glove_resources
        self.yolo               = Yolo(self.yolo_resources)
        # self.scene              = SceneDetection(self.scene_resources)
        self.quote              = Quotes(self.quote_resources)
        self.glove              = GloveVectors(self.glove_resources)
        self.google_images      = ImageSearch()
        self.mime               = Magic(mime=True)

        app.logger.info('Initiating SANDI pipeline')

        if self.folder:
            app.logger.debug('Retrieving image names')

            # Retrieve image names
            with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TAGS), 'r') as f:
                self.image_names = [line.split('\t').pop(0) for line in f]
        else:
            # Create directory to store results and images
            self.create_data_folder()

        app.logger.info('Finished initiating SANDI pipeline')

    def run_tags(self):
        """Runs the Yolo and Scene detection applications
        and saves the results to run image to text optimization

        Returns:
            list: images with missing tags
                  e.g. [{'file_name': file_name,
                          'data': byte64_string,
                          'type': mime-type
                         }, ...]
        """
        app.logger.info('Retrieving tags from images')

        yolo_tags           = dict()
        google_tags         = dict()
        images_missing_tags = list()

        args_tags = (self.image_names, os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))

        if self.num_images > 0:

            pool = ThreadPool(2)

            # Obtain tags from the yolo and scene detection models
            yolo_thread   = pool.apply_async(self.yolo.run, args_tags)
            google_thread = pool.apply_async(self.google_images.run, args_tags)
            # scene_detection_thread = pool.apply_async(self.scene.run, args_tags)

            yolo_tags   = yolo_thread.get()
            google_tags = google_thread.get()
            # scene_detection_tags = self.scene.run(*args_tags)

            pool.close()
            pool.join()

            app.logger.debug('Saving tags to: %s', self.folder)

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TAGS), 'w') as f:

            for file_name in self.image_names:

                union_tags = set()

                try:
                    union_tags.update(yolo_tags[file_name])
                except KeyError:
                    pass

                # try:
                #     union_tags.update(scene_detection_tags[file_name])
                # except KeyError:
                #     pass

                try:
                    union_tags.update(google_tags[file_name])
                except KeyError:
                    pass

                union_tags = [tag.strip().replace(' ', '_') for tag in union_tags]

                tags = SandiWorkflow.TAGS_DELIM.join(union_tags) or SandiWorkflow.TAGS_DELIM

                f.write('{file_name}\t{tags}\n'
                        .format(file_name=file_name, tags=tags))

                """Add file name and image data
                to list of images with missing tags
                """
                if not union_tags:
                    images_missing_tags.append(file_name)

        app.logger.info('Finished retrieving tags from images with {num_missing} images missing tags'
                        .format(num_missing=len(images_missing_tags)))

        return images_missing_tags

    def run_alignment(self, space_images_evenly=False):
        """Runs sandi image and text alignment
        application
        """

        app.logger.info("Getting optimized alignments")

        params = {'work_dir': self.folder, 'num_images': self.num_images}
        if space_images_evenly:
            params['space_images_evenly'] = space_images_evenly

        app.logger.debug("Alignment parameters are: working directory: {work_dir}, number images {num_images}, space images evenly {space_images_evenly}"
                         .format(work_dir=self.folder, num_images=self.num_images, space_images_evenly=space_images_evenly))

        try:
            response = requests.get(url=SandiWorkflow.SANDI_ALIGNMENT_URI, params=params)
        except Exception as e:
            app.logger.exception(e)

        app.logger.info("Finished getting optimized alignments")

    def get_optimized_alignments(self, quotes=None):
        """Get alignment from 'path/to/alignments.txt'
            quotes ([dict], optional): Defaults to None. match of quote to image

        Raises:
            Exception: 'path/to/alignments.txt' does not exist

        Returns:
            dict: maps paragraph number to image name
                e.g. {para_id, filename, ...}
        """

        app.logger.info('Getting optimized alignments')

        results        = list()
        quote_used     = dict()
        alignments     = dict()
        alignment_path = os.path.join(self.folder, SandiWorkflow.FILENAME_ALIGN)

        # Check that alignment file exists
        if not os.path.exists(alignment_path):
            raise Exception('file "{path}" does not exist' \
                .format(path=alignment_path))

        # Read alignments from alignments.txt
        with open(alignment_path) as f:
            for line in f:
                align = line.split('\n')[0].split('\t')
                alignments[int(align[0])-1] = align[1]

        results = self.get_alignments(alignments, quotes)

        app.logger.info('Finished getting optimized alignments')

        return results

    def get_randomized_alignments(self, quotes=None):
        """Randomly assigns at most one image to one paragraph
            quotes (dict, optional): Defaults to None. {filename: quote, ...}

        Returns:
            list: elements are either text or images with quotes if given
        """
        app.logger.info('Getting randomized alignments')

        alignments  = dict()

        # sample random numbers
        random_samples = random.sample(range(0, self.num_texts-1), self.num_images)

        for image_ind, para_ind in enumerate(random_samples):
            alignments[para_ind] = self.image_names[image_ind]

        results = self.get_alignments(alignments, quotes)

        app.logger.info('Finished getting randomized alignments')

        return results

    def get_alignments(self, alignments, quotes):
        """Aligns paragraphs and images based off of
        alignments mapping

        Args:
            alignments (dict): mapping of paragraph number to image name
            quotes (dict): quotes for each paragraph

        Returns:
            list: aligned text and images
        """

        app.logger.info('Aligning images and texts')

        paragraphs  = list()
        results     = list()
        quote_used  = dict()

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TEXT), 'r') as f:
            paragraphs = [line.decode('utf8').split('\t').pop() for line in f]

        """
        We append paragraphs and any images
        that are aligned that paragraph
        """
        for i, paragraph in enumerate(paragraphs):
            results.append(paragraph)

            app.logger.debug('Appending paragraph {}'.format(i))

            if i in alignments:

                app.logger.debug('Appending {image} to paragraph {para}'.format(image=alignments[i], para=i))

                file_name   = alignments[i]
                file_path   = os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER, file_name)

                """Read in image as base64 string
                and append to results
                """
                with open(file_path, 'r') as image:

                    result = {'file_name'   : file_name,
                              'data'        : base64.b64encode(image.read()).decode('ascii'),
                              'type'        : self.mime.from_file(file_path),
                              'quote'       : None
                            }

                    results.append(result)

                    """ Find best quote with best
                    cosine similarity to paragraph
                    """
                    if quotes:

                        result['quote'] = self.get_best_quote(paragraph, quotes[file_name], quote_used)

                        app.logger.debug('Appending quote {quote} with {file_name} to \
                                          paragraphs {i}'.format(quote=result['quote'],
                                                                 file_name=result['file_name'],
                                                                 i=i))

        app.logger.info('Finished aligning images and texts')

        return results

    def get_quotes(self):
        """Runs quote suggestion applicaiton

        Returns:
            dict: {file name: [quote1, quote2, ...], ...}
        """
        quotes = self.quote.run(self.image_names, os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))

        return quotes

    def get_best_quote(self, paragraph, quotes, quote_used):
        """Finds best matching quote to paragraph
        based off of cosine similarity scores

        Args:
            paragraph (str): paragraph to match
            quotes (list: list of quotes to parase through
            quote_used (dict): quotes that have already been used

        Returns:
            str: quote most related to paragraph and not chosen before
        """

        top_score        = 0.0
        top_quote        = None
        vector_quote     = None
        vector_paragraph = self.glove.sentence_to_vec(paragraph)

        for quote in quotes:

            # do not include duplicates
            if quote in quote_used:
                continue

            vector_quote    = self.glove.sentence_to_vec(quote)
            score           = self.glove.cosine(vector_paragraph, vector_quote)

            # update quote with closest match
            if score > top_score:
                top_quote = quote

        return top_quote

    def get_cosine_similarities(self):
        """Retrives the image to paragraph cosine
        similarities outputted from the SANDI Servlet

        Returns:
            dict: map image-paragraph cosine similarities for each image
        """

        app.logger.info('Starting to retrieve cosine similarities between text and images')

        cosine_similarities      = dict()
        cosine_similarities_path = os.path.join(self.folder, 'cosine.txt')

        try:
            with open(cosine_similarities_path) as f:
                cosine_similarities = json.load(f)

            """
            Converts each mapping of image name to dict
            to a mapping of image name to list of cosine
            similarities in paragraph index order
            """
            for image_name, para_cosine_map in cosine_similarities.items():
                indices = sorted(para_cosine_map.keys(), key=lambda para: int(para))
                cosine_similarities[image_name] = ['{0:.3f}'.format(para_cosine_map[indice]) for indice in indices]

        except IOError as e:
            app.logger.warn('Cosine similarities path DNE: {path}'.format(path=cosine_similarities_path))

        app.logger.info('Finished retrieving cosine similarities between text and images')

        return cosine_similarities

    def get_topk_concepts(self):

        app.logger.info('Starting to retrieve top-k concepts between text and images')

        topk_concepts      = dict()
        topk_concepts_path = os.path.join(self.folder, 'topkParaConcept.txt')

        try:
            with open(topk_concepts_path) as f:
                topk_concepts = json.load(f)

            """
            Combines concepts together into
            one string for the concepts of
            each image
            """
            for image_name, concepts in topk_concepts.items():
                topk_concepts[image_name] = ', '.join(concepts)
                # TODO: remove hard-coded 'a'
                try:
                    topk_concepts[image_name].remove('a')
                except ValueError as e:
                    continue

        except IOError as e:
            app.logger.warn('Top-k concepts path DNE: {path}'.format(path=topk_concepts_path))

        app.logger.info('Finished retrieving top-k concepts between text and images')

        return topk_concepts

    def collect_uploaded_images(self, uploaded_images):
        """Save images from user to local filesystem

        Args:
            uploaded_images (list): list of flask image objects
        """
        app.logger.debug('Savings images')

        for upload in uploaded_images:

            upload.save(os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER, upload.filename))

            self.image_names.append(upload.filename)

        self.num_images = len(self.image_names)

        app.logger.info('Collected {num_images} images'.format(num_images=len(uploaded_images)))

        return self.num_images

    def collect_uploaded_text_files(self, uploaded_text_files):
        """Save texts from user to local filesystem

        Args:
            uploaded_text_files (list): list of flask text files
        """
        app.logger.debug('Saving paragraphs from files')

        paragraphs = list()

        for input_text in uploaded_text_files:
            paragraphs += input_text.read().decode('cp1252').splitlines()

        self.num_texts = len(paragraphs)

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TEXT), 'w') as f:
            for index, paragraph in enumerate(paragraphs):
                f.write('{index}\t{paragraph}\n'.format(index=index+1, paragraph=paragraph.encode('utf8')))

        app.logger.info('Collected {num_texts} paragraphs'.format(num_texts=self.num_texts))

        return self.num_texts

    def collect_uploaded_text(self, uploaded_text):

        app.logger.debug('Saving paragraphs from text input')

        paragraphs = filter(None, uploaded_text.splitlines())

        app.logger.debug(paragraphs)

        self.num_texts = len(paragraphs)

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TEXT), 'w') as f:
            for index, paragraph in enumerate(paragraphs):
                f.write('{index}\t{paragraph}\n'.format(index=index+1, paragraph=paragraph.encode('utf8')))

        app.logger.info('Collected {num_texts} paragraphs'.format(num_texts=self.num_texts))

        return self.num_texts

    def collect_missing_tags(self, form):
        """Save tags from user to local filesystem

        Args:
            form (ImmutableMultiDicti): Tuple mapping of filename to tags

        Returns:
            dict: maps filename to tags
        """

        app.logger.debug('Saving tags')

        user_tags = form.to_dict()

        app.logger.debug('full_tags {}'.format(user_tags))

        full_tags = dict()

        """Include only images with tags.
        If new valid tags are available, use those first.
        Other wise, if original tags are available, use those.
        The last case is to use an empty list indicating that
        we don't want this image to be included in the alignments.
        """
        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TAGS), 'r') as f:
            for line in f:
                line_split = line.split('\t')
                image_tags = filter(None, [tag.strip() for tag in line_split.pop().split(SandiWorkflow.TAGS_DELIM)])
                image_name = line_split.pop()

                try:
                    uploaded_tags = filter(None, [tag.strip().replace(' ', '_') for tag in user_tags[image_name].split(SandiWorkflow.TAGS_DELIM)])
                except:
                    pass

                if image_name in user_tags and uploaded_tags:
                    app.logger.debug('Using uploaded tags for image {image_name}: {tags}'.format(image_name=image_name, tags=uploaded_tags))
                    full_tags[image_name] = uploaded_tags
                elif image_tags:
                    app.logger.debug('Using current tags for image {image_name}: {tags}'.format(image_name=image_name, tags=image_tags))
                    full_tags[image_name] = image_tags
                else:
                    app.logger.debug('No tags for image {image_name}'.format(image_name=image_name))
                    full_tags[image_name] = list()

        with open(os.path.join(self.folder, SandiWorkflow.FILENAME_TAGS), 'w') as f:
            for file_name, tags in full_tags.items():

                new_tags = SandiWorkflow.TAGS_DELIM.join(tags) or SandiWorkflow.TAGS_DELIM

                f.write('{file_name}\t{tags}\n'
                        .format(file_name=file_name, tags=new_tags))

        app.logger.info('Collected tags from user')

        return full_tags

    def create_data_folder(self):
        """Create transient folder to store images, text, and results
        """
        app.logger.debug('Creating data directory')

        self.folder = None
        folder_ind = 0
        while True:
            try:
                self.folder = os.path.join(SandiWorkflow.TEMP_DATA_PATH, str(folder_ind))
                os.mkdir(self.folder)
                os.mkdir(os.path.join(self.folder, SandiWorkflow.IMAGES_FOLDER))
                break
            except OSError:
                folder_ind += 1
                pass

        app.logger.debug('Data directory created at {dir}'.format(dir=self.folder))

    def clean_up(self):
        """Remove transient folder
        """
        app.logger.debug('Erasing data directory')

        try:
            shutil.rmtree(self.folder)
        except Exception:
            pass

    @staticmethod
    def load_yolo_resources():
        """Loads in YoloV2 model

        Returns:
            model: YoloV2 model
        """
        return Yolo.load_resources()

    @staticmethod
    def load_scene_resources():
        """Loads in resourecs needed for scene detection

        Returns:
            tuple: (neural_network, transformer, labels)
        """
        # return SceneDetection.load_resources()
        return None

    @staticmethod
    def load_quote_resources():
        """Loads in resources needed for quote suggestions

        Returns:
            tuple: (model, neural_network, captions, vectors)
        """
        return Quotes.load_resources()

    @staticmethod
    def load_glove_resources():
        """Loads in resources needed for glove vector cosine similarity

        Returns:
            pandas.DataFrame: dataframe of vectors
        """
        return GloveVectors.load_resources()