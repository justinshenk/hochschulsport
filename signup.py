import argparse

def main():
    parser = ArgumentParser()
    parser.add_argument(name='first_name', type=str, required=False, help='Your\
            first name for registration.')
    parser.add_argument(name='last_name', type=str, required=False, help='Your\
            last name for registration.')
    parser.add_argument(name='email', type=str, required=False, help='Your\
            (university) email.')
    parser.add_argument(name='mat_nr', type=int, required=False, help='Your\
            matriculation number.')

if __name__ == "__main__":
    main()
