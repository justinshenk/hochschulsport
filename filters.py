"""
This module contains all filters which can be used to extract the elements
containing links and course names. Add a new one in case the website ever changes
"""

from bs4 import BeautifulSoup
from course import Course

def course_links_early_ss17(html):
    soup = BeautifulSoup(html)
    a_elems = soup.select('dl.bs_menu > dd a')
    links = map(lambda l: l.attrs['href'], a_elems) 
    names = map(lambda l: l.text, a_elems)
    return list(links), list(names)

"""
Extract specialisations of a course from its page
"""
def course_filter_detail_early_ss17(html):
    soup = BeautifulSoup(html)
    name = soup.find('div', class_='bs_head').text
    rows = soup.select('table.bs_kurse tbody tr')
    courses = []
    for row in rows:
        course_row = row.find('input')
        if not course_row or not course_row.attrs['value'] in ['Warteliste', 'buchen',
                'Vormerkliste']:
            import sys; sys.stderr.write('Skipping {}...\n'.format(name))
            continue
        else:
            id = course_row.attrs['name']
            course_name = name + ' ' + row.find('td', class_='bs_sdet').text
            time = row.find('td', class_='bs_stag').text + ' ' + row.find('td', class_='bs_szeit').text
            courses.append(Course(id, course_name, time=time))
    return courses
