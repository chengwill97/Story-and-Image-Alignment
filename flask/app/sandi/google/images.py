from app import app

import requests
import webbrowser
import pycurl
from bs4 import BeautifulSoup
from StringIO import StringIO

class ImageSearch:
    """Finds image descriptions from
    Google Reverse Image Search

    Returns:
        None
    """

    SEARCH_BY_IMAGE_URL = os.environ['SEARCH_BY_IMAGE_URL']
    USER_AGENT          = os.environ['USER_AGENT']

    def __init__(self):
        pass

    def run(self, file_names, image_dir:

        app.logger.info('Starting Google Reverse Image Search analysis')

        google_tags = dict()

        for file_name in file_names:

            image_path = os.path.join(images_dir, file_name)

            google_tags[file_name] = set(search_image(image_path))

            app.logger.debug('Google tags {file_name}: {results}'.format(file_name=file_name, results=google_tags[file_name]))

        app.logger.info('Finished Google Reverse Image Search analysis')

        return google_tags

    def search_image(self, image_path):
        """Search tags for a single image
        through Google Reverse Image Search

        Args:
            image_path (str): full path to image

        Returns:
            list: tags for image
        """


        tags = list()

        with open(image_path, 'rb') as image:

            multipart = {'encoded_image': (image_path, image),
                         'image_content': ''}

            response = requests.post(ImageSearch.SEARCH_BY_IMAGE_URL,
                                     files=multipart,
                                     allow_redirects=False)

            search_url = response.headers['Location']

            html_page = StringIO()

            conn = pycurl.Curl()
            conn.setopt(conn.URL, search_url)
            conn.setopt(conn.FOLLOWLOCATION, 1)
            conn.setopt(conn.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                                         AppleWebKit/537.11 (KHTML, like Gecko) \
                                         Chrome/23.0.1271.97 \
                                         Safari/537.11')
            conn.setopt(conn.WRITEFUNCTION, html_page.write)
            conn.perform()
            conn.close()

            soup = BeautifulSoup(html_page.getvalue(), 'html.parser')

            tags = soup.find('a', {'class': 'fKDtNb'}).string.split(' ')

        return tags