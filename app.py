import traceback
import logging.config

from flask import Flask
from flask import render_template, request, redirect
from sqlalchemy import desc

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
        limit(app.config["MAX_ROWS_SHOW"]).all()
        logger.debug("Index page accessed")
        return render_template('find.html', movies=movies)
    except:
        traceback.print_exc()
        logger.warning("Not able to display movies, error page returned")
        return render_template('error.html')


@app.route('/find', methods=['GET','POST'])
def find_movies():
    """Find similar movies given a POST with a movie input

    Returns: redirect to find page
    """

    try:
    
        if request.method == "POST":
            doubanId = request.form['doubanId']; imdbId = request.form['imdbId']
            title = request.form['title']
            order = request.form['order']

        # get movieId of requested movie
        if doubanId != '':
            # note that a javascript is already in placeto prevent non-integer input values
            doubanId = int(doubanId)
            query = "SELECT * FROM movies WHERE doubanId = {}".format(doubanId)
        elif imdbId != '':
            imdbId = int(imdbId)
            query = "SELECT * FROM movies WHERE imdbId = {}".format(imdbId)
        else:
            query = "SELECT * FROM movies WHERE title = '{}'".format(title)

        movie_requested = movie_manager.session.execute(query).first()

        # return movie not found page if the movie is not in the database
        if movie_requested == None: 
            logger.warning("The movie was not found, error page returned")
            return render_template('notfound.html')

        movieId = movie_requested[0] # get first movie matching the condition

        # get similar movies
        query = "SELECT * FROM predictions WHERE movieId = {}".format(movieId)
        similar_movies_list = movie_manager.session.execute(query).first()[1:]
        similar_movies = tuple(similar_movies_list)

        if order == "popularity": # rank by popularity
            similar_movies = movie_manager.session.query(Movies).filter(Movies.movieId.in_(similar_movies)).\
            order_by(desc(Movies.popularity)).all()
        elif order == "rating": # rank by rating
            similar_movies = movie_manager.session.query(Movies).filter(Movies.movieId.in_(similar_movies)).\
            order_by(desc(Movies.rating)).all()
        else: # default rank by similarity
            similar_movies = movie_manager.session.query(Movies).filter(Movies.movieId.in_(similar_movies)).all()
            similar_movies = sorted(similar_movies, key=lambda o: similar_movies_list.index(o.movieId))

        logger.debug("Find page accessed")

        return render_template('find.html', movies=similar_movies) 
    except:
        traceback.print_exc()
        logger.warning("Not able to display movies, error page returned")
        return render_template('error.html')


@app.route('/douban/')
def redirect_to_douban():
    """Redirects to the Douban page of a movie based on the Douban ID"""

    doubanId = request.args.get("doubanId")
    return redirect("https://movie.douban.com/subject/{}/".format(doubanId))

@app.route('/imdb/')
def redirect_to_imdb():
    """Redirects to the IMDB page of a movie based on the IMDB ID"""

    imdbId = request.args.get("imdbId")
    return redirect("https://www.imdb.com/title/tt{}/".format(imdbId))

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
