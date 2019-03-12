import os
import base64
import traceback

from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import session

from magic import Magic

from app import app

from app.sandi.demo import SandiWorkflow


@app.before_first_request
def initServer():
    """Initialize the models and neural nets used for
        Yolo,
        Scene detection,
        and Quote Suggestions
        only before the first request
    """
    app.logger.info('Setting up server')

    temp_data_path = app.config.get('TEMP_DATA_PATH')

    app.logger.debug('Setting up data directory {}'.format(temp_data_path))

    try:
        os.mkdir(temp_data_path)
    except OSError:
        if not os.path.isdir(temp_data_path):
            app.logger.warn('Error creating directory {}'
                            .format(temp_data_path))

    app.logger.debug('Setting up models and nets')

    global yolo_resources, scene_resources, quote_resources, glove_resources
    yolo_resources = SandiWorkflow.load_yolo_resources()
    scene_resources = SandiWorkflow.load_scene_resources()
    quote_resources = SandiWorkflow.load_quote_resources()
    glove_resources = SandiWorkflow.load_glove_resources()

    app.logger.info('Server set up')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page of sandi web app

    Returns:
        template: template of home page
    """
    app.logger.info('Starting new session')

    # Start new session by clearing previous session variables
    session.clear()

    return render_template('homepage.html')


@app.route('/examples/', defaults={'examples_id': None},
           methods=['GET', 'POST'])
@app.route('/examples/<examples_id>', methods=['GET', 'POST'])
def examples(examples_id):
    """Examples page of sandi web app

    Returns:
        template: template of examples page
    """
    examples_path = app.config.get('EXAMPLES_PATH')
    examples_folders = list()
    images = list()
    text = ''
    mime = Magic(mime=True)

    # Start new example session
    session.clear()

    # Get list of examples in directory of examples
    examples_folders = [example for example in os.listdir(examples_path)
                        if os.path.isdir(os.path.join(examples_path, example))]
    examples_folders.sort(key=int)

    app.logger.debug(examples_folders)

    if not examples_id:
        try:
            examples_id = examples_folders[0]
        except IndexError:
            pass

    # Read in images from examples folder
    images_path = os.path.join(
        examples_path, examples_id, SandiWorkflow.IMAGES_FOLDER)

    for file_name in os.listdir(images_path):
        file_path = os.path.join(images_path, file_name)

        with open(file_path, 'r') as image:
            images.append({'file_name': file_name,
                           'data': base64.b64encode(image.read())
                                         .decode('ascii'),
                           'type': mime.from_file(file_path)
                           })

    # Read in text from examples folder
    with open(os.path.join(examples_path,
                           examples_id,
                           SandiWorkflow.FILENAME_TEXT), 'r') as f:
        text = '\n'.join([line.decode('utf8').split('\t').pop() for line in f])

    session['examples_id'] = examples_id

    app.logger.info('Returning template of example {examples_id}'.format(
        examples_id=examples_id))

    return render_template('examples.html',
                           examples_id=examples_id,
                           num_examples=len(examples_folders),
                           examples_folders=examples_folders,
                           images=images,
                           text=text)


@app.route('/demo/examples/process', methods=['GET', 'POST'])
def examples_process():
    """Set up example and
    redirect to demo
    """
    examples_id = session.get('examples_id', '')
    examples_path = app.config.get('EXAMPLES_PATH')
    examples_folder = os.path.join(examples_path, examples_id)
    examples_images = os.path.join(
        examples_folder, SandiWorkflow.IMAGES_FOLDER)
    demo_folder = None
    tags = dict()

    app.logger.info('Setting up example {examples_id}'.format(
        examples_id=examples_id))

    if request.method == 'GET':
        return render_template('index.html')

    # Set up demo from examples resources
    demo = SandiWorkflow()
    demo_folder = demo.folder
    demo_images = os.path.join(demo_folder, SandiWorkflow.IMAGES_FOLDER)
    examples_images = os.path.join(
        examples_path, examples_id, SandiWorkflow.IMAGES_FOLDER)
    examples_tags_file = os.path.join(
        examples_folder, SandiWorkflow.FILENAME_TAGS)
    demo_tags_folder = os.path.join(demo_folder, SandiWorkflow.FILENAME_TAGS)

    """
    Copy tags.txt with selected images
    as well as images over to data folder
    """
    with open(examples_tags_file, 'r') as f:
        for line in f:
            line_split = line.split('\t')
            line_tags = line_split.pop().split(SandiWorkflow.TAGS_DELIM)
            image_name = line_split.pop()
            image_tags = filter(None, [tag.strip() for tag in line_tags])

            # Copy image from examples folder to demo folder
            if image_name in request.form:
                tags[image_name] = image_tags

                src_path = os.path.join(examples_images, image_name)
                dst_path = os.path.join(demo_images, image_name)

                os.link(src_path, dst_path)

    # Copy tags with images that were selected
    with open(demo_tags_folder, 'w') as f:
        for file_name, image_tags in tags.items():

            new_tags = SandiWorkflow.TAGS_DELIM.join(
                image_tags) or SandiWorkflow.TAGS_DELIM

            f.write('{file_name}\t{tags}\n'
                    .format(file_name=file_name, tags=new_tags))

    # Gather and text
    if 'use_text' in request.form:
        num_texts = demo.collect_uploaded_text(request.form.get('text', ''))
    else:
        num_texts = demo.collect_uploaded_text_files(
            request.files.getlist('text_files'))

    num_images = len(tags)

    # Retrieve the number of images to include in the alignment
    try:
        request_num_images = int(request.form.get(
            'include_num_images', num_images))
    except Exception:
        request_num_images = num_images

    # Default to number of images uploaded if num_images out of range
    num_images = min(request_num_images, num_images)

    demo.num_images = num_images

    app.logger.debug('User requests to have {request_num_images} images'
                     .format(request_num_images=request_num_images))
    app.logger.debug('Application set to have {num_images} images'
                     .format(num_images=num_images))

    """Set appropriate session
    variables for demo route
    """
    session['folder'] = demo.folder
    session['num_images'] = num_images
    session['num_texts'] = num_texts
    session['include_quotes'] = 'include_quotes' in request.form
    session['space_images_evenly'] = 'space_images_evenly' in request.form
    session['from_example'] = True

    app.logger.info('Example {examples_id}'.format(examples_id=examples_id))

    return redirect(url_for('process_demo'))


@app.route('/demo/imagesMissingTags', methods=['GET', 'POST'])
def images_missing_tags():
    """Requests tags for images without tags

    Returns:
        template: template to get more tags
    """
    folder = session.get('folder', None)
    file_names = list()
    images_missing_tags = list()
    mime = Magic(mime=True)

    if not folder:
        return redirect(url_for('index'))

    try:
        file_names = request.args.getlist('images_missing_tags')
    except KeyError:
        pass

    # Read image data
    for file_name in file_names:
        file_path = os.path.join(
            folder, SandiWorkflow.IMAGES_FOLDER, file_name)

        with open(file_path, 'r') as image:
            images_missing_tags.append(
                {'file_name': file_name,
                 'data': base64.b64encode(image.read()).decode('ascii'),
                 'type': mime.from_file(file_path)
                 })

    app.logger.debug('images_missing_tags')

    return render_template('images_missing_tags.html',
                           images_missing_tags=images_missing_tags)


@app.route('/demo/results', methods=['GET', 'POST'])
def process_demo():
    """Page with results of sandi demo

    Returns:
        template: template of demo with results
                  or page to request more tags
    """
    app.logger.info('Handling Demo Request')

    folder = session.pop('folder', None)
    num_images = session.pop('num_images', 0)
    num_texts = session.pop('num_texts', 0)
    include_quotes = session.pop(
        'include_quotes', 'include_quotes' in request.form)
    space_images_evenly = session.pop(
        'space_images_evenly', 'space_images_evenly' in request.form)
    from_example = session.pop('from_example', False)

    if request.method == 'GET' and not from_example:
        return render_template('demo.html', num_images=0, num_texts=0,
                               results=list())

    # Initialize workflow for SANDI demo
    demo = SandiWorkflow(folder=folder,
                         num_images=num_images,
                         num_texts=num_texts,
                         yolo_resources=yolo_resources,
                         scene_resources=scene_resources,
                         quote_resources=quote_resources,
                         glove_resources=glove_resources)

    app.logger.debug('Session contains folder: {folder}'.format(folder=folder))

    """Handles start of a new session
    including extracting images and text
    from the user input as well as other
    input, i.e. checkboxes and ranges.
    """
    if folder is None:
        # Gather and save images
        num_images = demo.collect_uploaded_images(
            request.files.getlist('images'))

        # Gather and text
        if 'use_text' in request.form:
            num_texts = demo.collect_uploaded_text(
                request.form.get('text', ''))
        else:
            num_texts = demo.collect_uploaded_text_files(
                request.files.getlist('text_files'))

        # Retrieve the number of images to include in the alignment
        try:
            request_num_images = int(request.form.get(
                'include_num_images', num_images))
        except Exception:
            request_num_images = num_images

        # Default to number of images uploaded if num_images out of range
        num_images = min(request_num_images, num_images)

        demo.num_images = num_images

        app.logger.debug('User requests to have {request_num_images} images'
                         .format(request_num_images=request_num_images))
        app.logger.debug('Application set to have {num_images} images'
                         .format(num_images=num_images))

        # Get tags from yolo and caffe
        images_missing_tags = demo.run_tags()

        # Fill in session information for manuel tag entry
        if images_missing_tags:
            app.logger.info('Could not retrieve tags for some images')

            session['folder'] = demo.folder
            session['num_images'] = num_images
            session['num_texts'] = num_texts
            session['include_quotes'] = 'include_quotes' in request.form
            session['space_images_evenly'] = 'space_images_evenly'\
                                             in request.form

            return redirect(url_for('images_missing_tags',
                                    images_missing_tags=images_missing_tags))

    elif not from_example:
        app.logger.info('Gathering tags from user')

        # Get new tags here
        demo.collect_missing_tags(request.form)

    demo.run_alignment(space_images_evenly=space_images_evenly)

    app.logger.debug('Include quotes: {include_quotes}'.format(
        include_quotes=include_quotes))

    app.logger.debug('Demo story_id: {story_id}'.format(
        story_id=demo.story_id))

    # Get reccomended quotes
    demo.get_quotes(include_quotes=include_quotes)

    return redirect(url_for('display_story', story_id=demo.story_id))


@app.route('/demo/story', methods=['GET', 'POST'])
def display_story():

    app.logger.info('Starting to display story')

    results = list()
    cosine_similarities = dict()
    topk_concepts = dict()
    quotes = dict()
    num_images = 0
    num_texts = 0
    story_id = request.args.get('story_id', None)

    app.logger.info('story_id: {story_id}'.format(story_id=story_id))

    if not story_id:
        return render_template('demo.html', num_images=0, num_texts=0,
                               results=results)

    demo = SandiWorkflow(story_id=story_id,
                         quote_resources=quote_resources,
                         glove_resources=glove_resources)

    # Get reccomended quotes
    quotes = demo.get_quotes()

    """Get optimized images and texts, and
    if alignment somehow fails, we give
    a randomized order of images and texts
    """
    try:
        # Gather results then analysis of said results
        results = demo.get_optimized_alignments(quotes=quotes)
        cosine_similarities = demo.get_cosine_similarities()
        topk_concepts = demo.get_topk_concepts()
    except Exception as e:
        # Randomize results in case of exception
        app.logger.warn(e)
        traceback.print_exc()
        results = demo.get_randomized_alignments(quotes=quotes)

    images = demo.get_images()
    tags = demo.get_tags()
    num_images = len(results)
    num_texts = sum(1 if result['file_name'] else 0 for result in results)

    app.logger.info('Finished displaying story')

    return render_template('demo.html',
                           num_images=num_images,
                           num_texts=num_texts,
                           results=results,
                           images=images,
                           tags=tags,
                           cosine_similarities=cosine_similarities,
                           topk_concepts=topk_concepts)
