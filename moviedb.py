import os
import urllib.parse

import requests


MOVIE_DB_KEY = os.environ.get('MOVIE_DB_KEY')
MOVIE_DB_API = 'https://api.themoviedb.org/3/'


def search_movie(query):
    q = urllib.parse.quote(query)
    res = make_request(f"{MOVIE_DB_API}search/movie?api_key={MOVIE_DB_KEY}&query={q}")
    return res["results"]


def get_movie_details(movie_id):
    return make_request(f"{MOVIE_DB_API}movie/{movie_id}?api_key={MOVIE_DB_KEY}")


def make_request(url):
    res = requests.get(url=url)
    res.raise_for_status()
    return res.json()
