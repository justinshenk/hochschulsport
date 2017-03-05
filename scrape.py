#!/usr/bin/env python3
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
import argparse

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
        if not course_list_url:
            raise ValueError('Cannot scrape without URL')
        if not course_link_filter:
            raise ValueError('Cannot scrape without course link filter')
            raise ValueError('Cannot scrape without course detail filter')
        self._course_list_url = course_list_url
        self._course_link_filter = course_link_filter
        self._course_filter = course_filter
        self._fname = fname
        self._courses = None

    @property
    def courses(self):
        if not self._courses:
            stderr.write(('Courses not loaded, '
                'attempting to read from {}...\n').format(self._fname))
            if not exists(self._fname):
                stderr.write('File not found, downloading...\n')
                self.update_courses()
            else:
                self.load_courses()
        return self._courses
        
    def save_courses(self):
        if not self._courses:
            raise RuntimeError('No courses loaded. Call update_courses() first.')
        with open(self._fname, mode='wb') as file:
            dump(self._courses, file)

    def load_courses(self):
        with open(self._fname, mode='rb') as file:
            self._courses = load(file)

    def update_courses(self, max_retries=5, timeout=20):
        """Extract courses from the index page.

        :return: list of Course objects
        """
        session = requests.Session()
        retry_adapter = HTTPAdapter(max_retries=5)
        session.mount(self._course_list_url, retry_adapter)
        html = session.get(self._course_list_url).text
        links, names = self._course_link_filter(html)
        links = list(map(lambda l: parse.urljoin(self._course_list_url, l), links))

        session = FuturesSession()
        # we assume the individual courses have the same prefix as the course
        # list
        parsed_url = parse.urlparse(self._course_list_url)
        prefix = parsed_url.scheme + '://' + parsed_url.netloc
        session.mount(prefix, retry_adapter)
        futures = []
        for i, l in enumerate(links):
            print('Processing {} ({} of {})'.format(l, i+1, len(links)))
            futures.append(session.get(l, timeout=timeout))

        self._courses = [course for lst in
                (self._course_filter(f.result().text) for f in futures if not
                    f.exception()) for course in lst]

def validate_args(args, config):
    """Check if each necessary argument is present in either cmdline args or
    config file

    :args: return value of ArgumentParser#parse_args()
    :config: ConfigParser() object
    :returns: Bool
    """
    pass

def main():
    parser = argparse.ArgumentParser(description='Scrape the Hochschulsport\
            website. The url is read from the zfh.conf or specified by\
            parameter.')
    parser.add_argument('--outfile', type=str, default='courses.pickle',
            required=False, help='File to save the course data to.')
    parser.add_argument('--index_url', type=str, required=False, 
            help='The web url listing all available courses.')
    parser.add_argument('--max_retries', type=int, choices=range(1,50),
            default=5, required=False, 
            help='Retries for obtaining individual courses')
    parser.add_argument('--timeout', type=int, choices=range(5,50),
            default=20, required=False, help='Timeout for requests.')
    args = parser.parse_args()

    # parser.add_argument(name='first_name', type=str, required=False, help='Your\
    #         first name for registration.')
    # parser.add_argument(name='last_name', type=str, required=False, help='Your\
    #         last name for registration.')
    # parser.add_argument(name='email', type=str, required=False, help='Your\
    #         (university) email.')
    # parser.add_argument(name='mat_nr', type=int, required=False, help='Your\
    #         matriculation number.')
    s = Scraper(args.index_url, course_links_early_ss17,
            course_filter_detail_early_ss17, fname=args.outfile)
    # s.update_courses(max_retries=args.max_retries, timeout=args.timeout)
    # s.update_courses()
    # s.save_courses()
    courses = s.courses
    for c in courses:
        print(c)

if __name__ == "__main__":
    main()
