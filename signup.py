#!/usr/bin/env python3

from argparse import ArgumentParser
from difflib import SequenceMatcher
import sys
import requests
import configparser

from course import CourseManager
from filters import extract_fid

def signup(course, post_url, user_data):
    if course.kind != 'buchen':
        raise RuntimeError('Currently, only booking is supported.')
    session = requests.Session()
    # do first request to get secret form values
    post_headers = {
            # 'Content-Length': ${Content-Length},
            'Cache-Control': 'max-age=0',
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
            }
    response1 = session.post(post_url, headers=post_headers, data=post_data,
            allow_redirects=False)
    fid = extract_fid(response1.text)
    import ipdb; ipdb.set_trace()


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
