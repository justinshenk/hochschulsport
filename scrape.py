import requests
from urllib import parse
from bs4 import BeautifulSoup
import pprint

def get_courses(course_list_url, course_filter):
    html = requests.get(course_list_url).text
    links, names = course_filter(html)
    for i, (l, n) in enumerate(zip(links, names)):
        if 'RESTPLÄTZE' in n:
            del links[i]
            del names[i]
    links = map(lambda l: parse.urljoin(course_list_url, l), links)
    return list(zip(links, names))

if __name__ == "__main__":

    course_list_url = 'https://buchung.zfh.uni-osnabrueck.de/angebote/aktueller_zeitraum/index.html'

    def filter(html):
        soup = BeautifulSoup(html)
        a_elems = soup.select('dl.bs_menu > dd a')
        links = map(lambda l: l.attrs['href'], a_elems) 
        names = map(lambda l: l.text, a_elems)
        return list(links), list(names)

    pprint.pprint(get_courses(course_list_url, filter))
