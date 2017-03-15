"""
This module contains all filters which can be used to extract the elements
containing links and course names. Add a new one in case the website ever changes
"""

from bs4 import BeautifulSoup
from course import Course
import re
import sys

def course_links_early_ss17(html):
    soup = BeautifulSoup(html)
    a_elems = soup.select('dl.bs_menu > dd a')
    links = map(lambda l: l.attrs['href'], a_elems) 
    names = map(lambda l: l.text, a_elems)
    return list(links), list(names)

def course_filter_detail_early_ss17(html, page_url):
    """
    Extract specialisations of a course from its page
    """
    soup = BeautifulSoup(html)
    name = soup.find('div', class_='bs_head').text
    rows = soup.select('table.bs_kurse tbody tr')
    courses = []
    for row in rows:
        course_row = row.find('input')
        if not course_row or not course_row.attrs['value'] in ['Warteliste', 'buchen',
                'Vormerkliste']:
            print('Skipping {}...'.format(name), file=sys.stderr)
            continue
        else:
            kind = course_row.attrs['value']
            bscode = extract_bscode(html)
            id = int(re.match(r'BS_Kursid_(\d+)', course_row.attrs['name']).group(1))
            course_name = name + ' ' + row.find('td', class_='bs_sdet').text
            time = row.find('td', class_='bs_stag').text + ' ' + row.find('td', class_='bs_szeit').text
            courses.append(Course(id, course_name, time=time, kind=kind,
                url=page_url, bs_code=bscode))
    return courses

def extract_fid(html):
    fid_input = BeautifulSoup(html).select('input[name="fid"]')
    if not fid_input:
        return None
    else:
        return fid_input[0].attrs['value']

def extract_bscode(html):
    """
    Get the BS_code from the course landing page
    """
    bscode_input = BeautifulSoup(html).select('input[name="BS_Code"]')
    if not bscode_input:
        return None
    else:
        return bscode_input[0].attrs['value']

def extract_price(html):
    """
    Get the price from the confirmation (not the initial signup) page
    """
    price_input = BeautifulSoup(html).select('input[name="preis_anz"]')
    if not price_input:
        return None
    else:
        return price_input[0].attrs['value']

def extract_formdata(html):
    """
    Get the hidden _formdata value from the confirmation (not the initial signup) page
    """
    formdata_input = BeautifulSoup(html).select('input[name="_formdata"]')
    if not formdata_input:
        return None
    else:
        return formdata_input[0].attrs['value']
    
