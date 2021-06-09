"""Script for running the app"""

import logging.config

from flask import Flask
from flask import render_template, request, redirect
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from src.add_movie import Movies, MovieManager

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

movie_manager = MovieManager(app)

@app.route('/')
def index():
    """About page of the app.

    Create view into index page that contains about info and
    instructions of the app using app/templates/index.html template.

    Returns: rendered html template
    """

    return render_template('index.html')



@app.route('/movies')
def show_movies():
    """Main view that lists movies in the database.

    Create view into index page that uses data queried from Movie database and
    inserts it into the msiapp/templates/find.html template.

    Returns: rendered html template
    """

    try:
        movies = movie_manager.session.query(Movies).order_by(desc(Movies.popularity)).\
        limit(app.config["MAX_ROWS_SHOW"]).all() # access the movies table
        logger.debug("Index page accessed")
        return render_template('find.html', movies=movies)
    except SQLAlchemyError as error:
        logger.warning("Not able to display movies, due to error: %s",
                        str(error.__dict__['orig']))
        return render_template('error.html')


@app.route('/find', methods=['GET','POST'])
def find_movies():
    """Find similar movies given a POST with a movie input

    Returns: redirect to find page
    """

    # find movie ID of requested movie
    try:
        if request.method == "POST":
            douban_id = request.form['doubanId']
            imdb_id = request.form['imdbId']
            title = request.form['title']
            order = request.form['order']

        if douban_id != '':
            # note that a javascript is already in place to prevent non-integer input values
            douban_id = int(douban_id)
            query = "SELECT movieid " + \
                    "FROM movies " + \
                    "WHERE doubanid = {}".format(douban_id)

        elif imdb_id != '':
            imdb_id = int(imdb_id)
            query = "SELECT movieid " + \
                    "FROM movies " + \
                    "WHERE imdbid = {}".format(imdb_id)
        else:
            query = "SELECT movieid " + \
                    "FROM movies " + \
                    "WHERE title = '{}'".format(title)

        movie_requested = movie_manager.session.execute(query).first()
    except SQLAlchemyError as error:
        logger.warning("Error encountered when finding requested movie: %s",
                    str(error.__dict__['orig']))
        logger.debug("Error page returned")
        return render_template('error.html')

    # return movie not found page if the movie is not in the database
    if movie_requested is None:
        logger.warning("The movie was not found, error page returned")
        return render_template('notfound.html')

    # fetch recommendations (similar movies)
    try:
        movie_id = movie_requested[0] # get first movie matching the condition

        # get similar movies
        query = "SELECT movieid, top1, top2, top3, top4, top5, top6, top7, top8, top9, top10 " + \
                "FROM predictions " + \
                "WHERE movieid = {}".format(movie_id)
        similar_movies_list = movie_manager.session.execute(query).first()[1:]
        similar_movies = tuple(similar_movies_list)

        if order == "popularity": # rank by popularity
            similar_movies = movie_manager.session.query(Movies).\
                            filter(Movies.movieId.in_(similar_movies)).\
                            order_by(desc(Movies.popularity)).all()
        elif order == "rating": # rank by rating
            similar_movies = movie_manager.session.query(Movies).\
                            filter(Movies.movieId.in_(similar_movies)).\
                            order_by(desc(Movies.rating)).all()
        else: # default rank by similarity
            similar_movies = movie_manager.session.query(Movies).\
                            filter(Movies.movieId.in_(similar_movies)).all()
            similar_movies = sorted(similar_movies,
                            key=lambda o: similar_movies_list.index(o.movieId))

        logger.debug("Find page accessed")

        return render_template('find.html', movies=similar_movies)
    except SQLAlchemyError as error:
        logger.warning("Error encountered when fetching recommendations: %s",
                        str(error.__dict__['orig']))
        return render_template('error.html')


@app.route('/douban/')
def redirect_to_douban():
    """Redirects to the Douban page of a movie based on the Douban ID"""

    # get the user requested id
    douban_id = request.args.get("doubanId")
    return redirect("https://movie.douban.com/subject/{}/".format(douban_id))

@app.route('/imdb/')
def redirect_to_imdb():
    """Redirects to the IMDB page of a movie based on the IMDB ID"""

    # get the user requested id
    imdb_id = request.args.get("imdbId")
    return redirect("https://www.imdb.com/title/tt{}/".format(imdb_id))

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
