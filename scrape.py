#!/usr/bin/env python3
"""
Module for scraping the Hochschulsport website
"""
from bs4 import BeautifulSoup
from urllib import parse
from pickle import dump, load
from os.path import exists
from requests_futures.sessions import FuturesSession
import requests
from requests.adapters import HTTPAdapter
import argparse
import configparser
import sys

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
            print(('Courses not loaded, '
                'attempting to read from {}...').format(self._fname),
                file=sys.stderr)
            if not exists(self._fname):
                print('File not found, downloading...', file=sys.stderr)
                self.update_courses()
            else:
                self.load_courses()
        return self._courses
        
    def save_courses(self):
        if not self._courses:
            raise RuntimeError('No courses loaded. Call update_courses() first.')
        try:
            with open(self._fname, mode='wb') as file:
                dump(self._courses, file)
        except IOError:
            raise RuntimeError('Could not write to {}'.format(self._fname))

    def load_courses(self):
        try:
            with open(self._fname, mode='rb') as file:
                self._courses = load(file)
        except IOError:
            raise RuntimeError('Could not read from {}'.format(self._fname))

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
    if args.update:
        if not args.index_url:
            try:
                args.index_url = config['global']['index_url']
            except KeyError:
                return (False, 'Error. Index url for update neither in params nor configuration file.')
    return (True, 'Arguments OK.')
    

def main():
    parser = argparse.ArgumentParser(description=('Scrape the Hochschulsport'
        'website. The url is read from the zfh.conf or specified by'
            'parameter.'))
    parser.add_argument('--outfile', type=str, default='courses.pickle',
            required=False, help='File to save the course data to.')
    parser.add_argument('--index_url', type=str, required=False, default=None,
            help='The web url listing all available courses.')
    parser.add_argument('--max_retries', type=int, choices=range(1,50),
            metavar='[1-50]',
            default=5, required=False, 
            help='Retries for obtaining individual courses')
    parser.add_argument('--timeout', type=int, choices=range(5,50),
            metavar='[5-50]',
            default=20, required=False, help='Timeout for requests.')
    parser.add_argument('--database', type=str, default='courses.pickle',
            required=False, help='File to store courses in.')
    parser.add_argument('--update', action='store_true', default=False,
            required=False, help='Update the database from web')
    parser.add_argument('--list', action='store_true', default=False,
            required=False, help='Print list of courses')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('zfh.conf')

    args_valid, msg = validate_args(args, config)
    if not args_valid:
        print(msg)
        exit(1)

    s = Scraper(args.index_url, course_links_early_ss17,
            course_filter_detail_early_ss17, fname=args.outfile)
    if args.update:
        s.update_courses(max_retries=args.max_retries, timeout=args.timeout)
        try:
            s.save_courses()
        except RuntimeError as e:
            print(e.message, file=sys.stderr)
            exit(2)

    if args.list:
        courses = s.courses
        for c in courses:
            print(c)

if __name__ == "__main__":
    main()
