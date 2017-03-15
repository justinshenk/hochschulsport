#!/usr/bin/env python3

from argparse import ArgumentParser
from difflib import SequenceMatcher
from urllib.parse import parse_qs
import sys
import requests
import configparser

from course import CourseManager
from filters import extract_fid, extract_price, extract_formdata

def signup(course, post_url, user_data):
    if course.kind != 'buchen':
        raise RuntimeError('Currently, only booking is supported.')
    session = requests.Session()
    # do first request to get secret form values
    post_headers = {
            'Cache-Control': 'no-cache',
            'Origin': 'https://buchung.zfh.uni-osnabrueck.de',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Referer': course.url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en,en-US;q=0.8,de;q=0.6',
            }
    post_data = {
            'BS_Kursid_{}'.format(course.id): course.kind,
            'BS_Code': course.bs_code
            }

    req1 = requests.Request('POST', post_url, headers=post_headers,
            data=post_data).prepare()

    print(req1.headers)
    print(req1.body)

    response1 = session.send(req1, allow_redirects=False)
    fid = extract_fid(response1.text)
    print('fid is {}'.format(fid))
    
    post_headers = {
            'Host': 'buchung.zfh.uni-osnabrueck.de',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'https://buchung.zfh.uni-osnabrueck.de',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Referer': course.url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en,en-US;q=0.8,de;q=0.6',
            }
    if course.kind == 'buchen':
        post_data = {
                'fid': fid,
                'sex': user_data['gender'],
                'vorname': user_data['first_name'],
                'name': user_data['last_name'],
                'strasse': user_data['address'],
                'ort': user_data['zipcode'] + ' ' + user_data['place'],
                'statusorig': 'Stud-UOS',
                'matnr': user_data['matnr'],
                'email': user_data['email'],
                'iban': user_data['iban'],
                'telefon': '',
                'kontoinh': 'nur+ändern,+falls+nicht+mit+Teilnehmer/in+identisch',
                'tnbed': '1 ',
                'tnbed2': '1'
                }
    elif course.kind == 'Warteliste':
        post_data = {
                'fid': fid,
                'Email': user_data['email']
                }

    req2 = requests.Request('POST', post_url, headers=post_headers,
            data=post_data).prepare()
    print(req2.headers)
    print(req2.body)

    response2 = session.send(req2, allow_redirects=False)

    price = extract_price(response2.text)
    formdata = extract_formdata(response2.text)
    print('price is {}'.format(price))
    print('_formdata is {}'.format(formdata))
    post_data.update({
        'Phase': 'final',
        'preis_anz': price,
        '_formdata': formdata
        })
    # delete unused params -- seems to make no difference
    # del post_data['tnbed2']
    # del post_data['kontoinh']
    # del post_data['iban']

    post_headers.update({ 'Referer':
        'https://buchung.zfh.uni-osnabrueck.de/cgi/anmeldung.fcgi' })

    req3 = requests.Request('POST', post_url, headers=post_headers,
            data=post_data).prepare()

    print(req3.headers)
    print(req3.body)
    response3 = session.send(req3, allow_redirects=False)
    print(response3.text)

def filter_courses(courses, query=None, id=None, fuzzy=False, num_results=10):

    if not query and not id:
        raise RuntimeError('Filter needs either name or id.')

    if id:
        good_courses = filter(lambda c: id == c.id, courses)
        return good_courses
    elif query:

        # compatibility function
        def course_match(course):
            """ Fuzzy or hard distance """

            if not fuzzy:
                return 1 - float(query.lower() in course.name.lower())
            else:
                return 1 - SequenceMatcher(None, list(course.name), list(query)).ratio()

        good_courses = sorted(courses, key=course_match)
        return good_courses[:num_results]


def main():
    parser = ArgumentParser(description='Sign up for a course.')
    parser.add_argument('--course_name', type=str, required=False, default=None,
            help='Name of the course')
    parser.add_argument('--course_id', type=int, required=False, default=None,
            help='Id of the course')
    parser.add_argument('--first_name', type=str, required=False, help=('Your'
            'first name for registration.'))
    parser.add_argument('--last_name', type=str, required=False, help=('Your'
        'last name for registration.'))
    parser.add_argument('--email', type=str, required=False, help=('Your'
        '(university) email.'))
    parser.add_argument('--mat_nr', type=int, required=False, help=('Your'
        'matriculation number.'))
    parser.add_argument('--database', type=str, default='courses.pickle',
            required=False, help='File to read courses from.')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('zfh.conf')

    if not args.course_name and not args.course_id:
        print('Error. Either name or id must be given.', file=sys.stderr)
        exit(1)
    else:
        courses = filter_courses(CourseManager.load_all(args.database),
                query=args.course_name, id=args.course_id)
        for i, c in enumerate(courses):
            print('{:4}: {}'.format(i, c.name))
        while True:
            try:
                num = int(input('Enter number for signup: '))
            except ValueError:
                continue
            if 0 <= num < len(courses):
                break
        print('Signing up for {}'.format(courses[num]))
        signup(courses[num], config['global']['post_url'], config['user'])

if __name__ == "__main__":
    main()
