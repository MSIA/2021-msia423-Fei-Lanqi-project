import traceback
import logging.config
from flask import Flask
from flask import render_template, request, redirect, url_for
from sqlalchemy import desc
import pandas as pd
import numpy as np

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session
from src.add_movie import Movies, MovieManager
movie_manager = MovieManager(app)

@app.route('/')
def index():
    """Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.

    Returns: rendered html template

    """

    try:
        movies = movie_manager.session.query(Movies).limit(app.config["MAX_ROWS_SHOW"]).all()
        logger.debug("Index page accessed")
        return render_template('index.html', movies=movies)
    except:
        traceback.print_exc()
        logger.warning("Not able to display movies, error page returned")
        return render_template('error.html')


@app.route('/find', methods=['POST'])
def find_movies():
    """Find similar movies given a POST with a movie input

    :return: redirect to output page
    """

    try:
        doubanId = parse_to_int(request.form['Douban ID'])
        imdbId = parse_to_int(request.form['IMDB ID'])

        # get movieId of requested movie
        if doubanId != "":
            query = "SELECT * FROM movies WHERE doubanId = {}".format(doubanId)
        else:
            query = "SELECT * FROM movies WHERE imdbId = {}".format(imdbId)

        movie_requested = movie_manager.session.execute(query).first(); movieId = movie_requested[0]

        # get similar movies
        query = "SELECT * FROM predictions WHERE movieId = {}".format(movieId)
        similar_movies = movie_manager.session.execute(query).first()[1:]
        similar_movies = tuple(similar_movies)

        similar_movies = movie_manager.session.query(Movies).filter(Movies.movieId.in_(similar_movies)).\
            order_by(desc(Movies.popularity)).all() # default rank by popularity

        logger.debug("Output page accessed")

        return render_template('output.html', movies=similar_movies)
    except:
        traceback.print_exc()
        logger.warning("Not able to display movies, error page returned")
        return render_template('error.html')

def parse_to_int(string):
    """Auxilliary function to help parse string input to integer."""

    try:
        string_int = int(string)
    except ValueError:
        print('Please enter an integer')
    
    return string_int


@app.route('/douban')
def redirect_to_douban(doubanId):
    return redirect("https://movie.douban.com/subject/{}/".format(doubanId))

@app.route('/imdb')
def redirect_to_imdb(imdbId):
    return redirect("https://www.imdb.com/title/tt{}/".format(imdbId))

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
