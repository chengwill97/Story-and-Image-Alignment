from app import app

import os
import requests
import pycurl
from bs4 import BeautifulSoup
from StringIO import StringIO

from multiprocessing.dummy import Pool as ThreadPool


class ImageSearch:
    """Finds image descriptions from
    Google Reverse Image Search

    Returns:
        None
    """

    SEARCH_BY_IMAGE_URL = os.environ['SEARCH_BY_IMAGE_URL']
    USER_AGENT          = os.environ['USER_AGENT']

    def __init__(self):
        self.images_dir  = None
        self.google_tags = None

    def run(self, file_names, images_dir):

        app.logger.info('Starting Google Reverse Image Search analysis')

        self.images_dir  = images_dir
        self.google_tags = dict()

        pool = ThreadPool(min(16, len(file_names)))
        pool.map(self.search_image, file_names)
        pool.close()
        pool.join()

        app.logger.info('Finished Google Reverse Image Search analysis')

        return self.google_tags

    def search_image(self, file_name):
        """Search tags with Google Reverse Image Search

        Send image to Google Reverse Image Search.
        Retrieve the redirect URL and get the
        corresponding HTML using pycurl and parsing
        it for the tags using BeautifulSoup.

        Args:
            image_path (str): full path to image

        Returns:
            list: tags for image
        """

        app.logger.info('Getting Google Tags for image {file_name}'.format(file_name=file_name))

        image_path = os.path.join(self.images_dir, file_name)

        tags = list()

        html_page = StringIO()

        with open(image_path, 'rb') as image:

            multipart = {'encoded_image': (image_path, image),
                         'image_content': ''}

            try:
                # Google search image
                response = requests.post(ImageSearch.SEARCH_BY_IMAGE_URL,
                                        files=multipart,
                                        allow_redirects=False)

                search_url = response.headers.get('Location')

                # Retrieve html results
                conn = pycurl.Curl()
                conn.setopt(conn.URL, search_url)
                conn.setopt(conn.FOLLOWLOCATION, 1)
                conn.setopt(conn.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                                            AppleWebKit/537.11 (KHTML, like Gecko) \
                                            Chrome/23.0.1271.97 \
                                            Safari/537.11')
                conn.setopt(conn.WRITEFUNCTION, html_page.write)
                conn.perform()

                # Parse html page for image description
                soup = BeautifulSoup(html_page.getvalue(), 'html.parser')

                tags = soup.find('a', {'class': 'fKDtNb'}).string.split(' ')

                tags = list(map(lambda tag: tag.lower(), tags))

            except requests.exceptions.RequestException as e:
                app.logger.warn('Request to get tags from Google Images failed')
                app.logger.warn(e)
            except pycurl.error as e:
                app.logger.warn('Performing pycurl connection failed')
                app.logger.warn(e)
            except Exception as e:
                app.logger.warn('Something unexpected happened')
                app.logger.warn(e)
            finally:
                conn.close()

        self.google_tags[file_name] = set(tags)

        app.logger.info('Received Google Tags: {tags}'.format(tags=tags))

        return