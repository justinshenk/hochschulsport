# hochschulsport
Super-fast auto-signup for Uos-Hochschulsport courses

# Status
Despite the fact that I replicate the browser's requests 1-1, this results in an
'unknown error' after the final `POST`. This makes no sense and can only be
attributed to dark magic.

* Use `scrape.py` to build a list of all available courses.
* Use `signup.py` with a `--course_name` (fuzzy-match, you will be prompted for the actual
  course) or `--course_id` (unique) to try (and fail) to signup.
