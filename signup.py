#!/usr/bin/env python3

from argparse import ArgumentParser
from difflib import SequenceMatcher
import sys

from course import CourseManager

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
    
    if not args.course_name and not args.course_id:
        print('Error. Either name or id must be given.', file=sys.stderr)
        exit(1)
    else:
        courses = filter_courses(CourseManager.load_all(args.database),
                query=args.course_name, id=args.course_id)
        for i, c in enumerate(courses):
            print('{:4}: {}'.format(i, c.name))

if __name__ == "__main__":
    main()
