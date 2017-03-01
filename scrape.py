"""
Module for scraping the Hochschulsport website
"""
from bs4 import BeautifulSoup
from urllib import parse
import pprint
import requests

from filters import filter_early_ss17
from course import Course

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
        
    def get_id(self, course_url):
        html = requests.get(course_url).text

    def get_courses(self):
        """Extract courses from the index page.

        :return: list of Course objects
        """
        html = requests.get(self._course_list_url).text
        links, names = self._course_filter(html)
        links = map(lambda l: parse.urljoin(course_list_url, l), links)
        all_courses = []

        def course_filter_detail(html):
            soup = BeautifulSoup(html)
            name = soup.find('div', class_='bs_head').text
            rows = soup.select('table.bs_kurse tbody tr')
            courses = []
            for row in rows:
                try:
                    id = row.find('input').attrs['name']
                except AttributeError:
                    continue
                else:
                    course_name = name + ' ' + row.find('td', class_='bs_sdet').text
                    time = row.find('td', class_='bs_szeit').text
                    courses.append(Course(id, course_name, time=time))
            return courses

        for l in links:
            html = requests.get(l).text
            all_courses.extend(course_filter_detail(html))

        return all_courses

if __name__ == "__main__":

    course_list_url = 'https://buchung.zfh.uni-osnabrueck.de/angebote/aktueller_zeitraum/index.html'
    s = Scraper(course_list_url, filter_early_ss17)
    courses = s.get_courses()
    for c in courses:
        print(c)
