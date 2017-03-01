"""
This module contains all filters which can be used to extract the elements
containing links and course names. Add a new one in case the website ever changes
"""

from bs4 import BeautifulSoup

def filter_early_ss17(html):
    soup = BeautifulSoup(html)
    a_elems = soup.select('dl.bs_menu > dd a')
    links = map(lambda l: l.attrs['href'], a_elems) 
    names = map(lambda l: l.text, a_elems)
    return list(links), list(names)
