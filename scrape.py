"""
Module for scraping the Hochschulsport website
"""
import requests
from urllib import parse
import pprint
from filters import filter_early_ss17

class Scraper(object):

    """Class to scrape yo ass."""

    def __init__(self, course_list_url, course_filter):
        """Create a new scraper

        :course_list_url: The URL wherein all current courses are listed
        :course_filter: Function of one parameter (the html text) which should
            extract (link, name) tuples from the html
        """
        self._course_list_url = course_list_url
        self._course_filter = course_filter
        

    def get_courses(self):
        """Extract courses from the index page.

        :return: list of tuple of (abs_link, name)
        """
        html = requests.get(self._course_list_url).text
        links, names = self._course_filter(html)
        for i, (l, n) in enumerate(zip(links, names)):
            if 'RESTPLÄTZE' in n:
                del links[i]
                del names[i]
        links = map(lambda l: parse.urljoin(course_list_url, l), links)
        return list(zip(links, names))

if __name__ == "__main__":

    course_list_url = 'https://buchung.zfh.uni-osnabrueck.de/angebote/aktueller_zeitraum/index.html'
    s = Scraper(course_list_url, filter_early_ss17)
    pprint.pprint(s.get_courses())
