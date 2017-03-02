"""
Module for scraping the Hochschulsport website
"""
from bs4 import BeautifulSoup
from urllib import parse
from pickle import dump, load
from sys import stderr
from os.path import exists
from requests_futures.sessions import FuturesSession
import requests
from requests.adapters import HTTPAdapter
import pprint

from filters import course_links_early_ss17, course_filter_detail_early_ss17
from course import Course

class Scraper(object):

    """Class to scrape yo ass."""

    def __init__(self, course_list_url, course_link_filter, course_filter, fname='courses.pickle'):
        """Create a new scraper

        :course_list_url: The URL wherein all current courses are listed
        :course_link_filter: Function of one parameter (the html text) which should
            extract (link, name) tuples from the html
        :course_filter: Function of one parameter (the html text) to extract
            from each course page the individual courses (there may be several time
            slots or different offerings)
        :fname: File name to save the courses in
        """
        self.__course_list_url = course_list_url
        self.__course_link_filter = course_link_filter
        self.__course_filter = course_filter
        self.__fname = fname
        self.__courses = None

    @property
    def courses(self):
        if not self.__courses:
            stderr.write(('Courses not loaded,'
                'attempting to read from {}...\n').format(self.__fname))
            if not exists(self.__fname):
                stderr.write('File not found, downloading...\n')
                self.update_courses()
            else:
                self.load_courses()
        return self.__courses
        
    def save_courses(self):
        with open(self.__fname, mode='wb') as file:
            dump(self.__courses, file)

    def load_courses(self):
        with open(self.__fname, mode='rb') as file:
            self.__courses = load(file)

    def update_courses(self):
        """Extract courses from the index page.

        :return: list of Course objects
        """
        session = requests.Session()
        retry_adapter = HTTPAdapter(max_retries=5)
        session.mount(self.__course_list_url, retry_adapter)
        html = session.get(self.__course_list_url).text
        links, names = self.__course_link_filter(html)
        links = list(map(lambda l: parse.urljoin(course_list_url, l), links))

        session = FuturesSession()
        # we assume the individual courses have the same prefix as the course
        # list
        parsed_url = parse.urlparse(self.__course_list_url)
        prefix = parsed_url.scheme + '://' + parsed_url.netloc
        session.mount(prefix, retry_adapter)
        futures = []
        for i, l in enumerate(links):
            print('Processing {} ({} of {})'.format(l, i+1, len(links)))
            futures.append(session.get(l, timeout=20))
            # all_courses.extend(self.__course_filter(html))

        self.__courses = [course for lst in
                (self.__course_filter(f.result().text) for f in futures if not
                    f.exception()) for course in lst]

if __name__ == "__main__":

    course_list_url = 'https://buchung.zfh.uni-osnabrueck.de/angebote/aktueller_zeitraum/index.html'
    s = Scraper(course_list_url, course_links_early_ss17,
            course_filter_detail_early_ss17)
    s.update_courses()
    courses = s.courses
    for c in courses:
        print(c)
