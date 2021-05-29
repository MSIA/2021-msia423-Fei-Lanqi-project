import os
import logging

import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Column, Integer, String, Float
from flask_sqlalchemy import SQLAlchemy
from numpy import genfromtxt


logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Base = declarative_base()

class Movies(Base):
    """Create a data model for the database to be set up for capturing movies."""

    __tablename__ = 'movies'

    movieId = Column(Integer, primary_key=True)
    doubanId = Column(Integer, unique=True, nullable=True)
    imdbId = Column(Float, unique=True, nullable=True)
    title = Column(String(100), unique=False, nullable=True)
    rating = Column(Float, unique=False, nullable=False)
    popularity = Column(Float, unique=False, nullable=False)
    
    def __repr__(self):
	    return '<Movie %r>' % self.title

class Predictions(Base):
    """Create a data model for the database for storing predictions."""

    __tablename__ = 'predictions'

    movieId = Column(Integer, primary_key=True)
    top1 = Column(Integer, unique=False, nullable=True)
    top2 = Column(Integer, unique=False, nullable=True)
    top3 = Column(Integer, unique=False, nullable=True)
    top4 = Column(Integer, unique=False, nullable=True)
    top5 = Column(Integer, unique=False, nullable=True)
    top6 = Column(Integer, unique=False, nullable=True)
    top7 = Column(Integer, unique=False, nullable=True)
    top8 = Column(Integer, unique=False, nullable=True)
    top10 = Column(Integer, unique=False, nullable=True)
    
    def __repr__(self):
	    return '<Prediction of %r>' % self.movieId

def create_db(engine_string: str) -> None:
    """Create database from provided engine string
    
    Args:
        engine_string: str - Engine string
    
    Returns: None
    """

    engine = sql.create_engine(engine_string) # set up mysql connection

    Base.metadata.create_all(engine) # create all tables

    logger.info("Database created.")


class MovieManager:
    
    def __init__(self, app=None, engine_string=None):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string
        """
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            engine = sql.create_engine(engine_string)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")

    def close(self) -> None:
        """Closes session
        Returns: None
        """
        self.session.close()

    def add_movie(self, movieId: int, doubanId: int, imdbId: int, title: str, rating: float, popularity: int, cluster: int) -> None:
        """Seeds an existing database with additional movies.
        Args:
            movieId: int - Id of movie
            doubanId: int - Douban id of movie
            imdbId: int - IMDB id of movie
            title: str - Title of movie
            rating: float - Average rating of movie
            popularity: float - Popularity of movie
        Returns:None
        """

        session = self.session
        movie = Movies(movieId=movieId, doubanId=doubanId, imdbId=imdbId, title=title, rating=rating, popularity=popularity)
        session.add(movie)
        session.commit()
        logger.info("Movie %s, added to database", title)

    def __load_data(self, file_name):
        """Auxilliary function for ingesting from csv."""

        data = genfromtxt(file_name, delimiter=',', skip_header=1)
        
        return data.tolist()

    def add_movie_from_csv(self, file_name):
        """Add movies to database from a csv file."""

        session = self.session

        try:
       
            data = self.__load_data(file_name) 

            for i in data:
                record = Movies(**{
                    'movieId' : i[0],
                    'doubanId' : i[1],
                    'imdbId' : i[2],
                    'title' : i[3],
                    'rating' : i[4],
                    'popularity' : i[5]
                })
                session.add(record) #Add all the records

            session.commit() #Attempt to commit all the records
        except:
            session.rollback() #Rollback the changes on error
        finally:
            session.close() #Close the connection
        
        logger.info("Movies from file {} are added to database".format(file_name))

    def add_prediction(self, movieId, pred) -> None:
        """Seeds an existing database with additional predictions.
        Args:
            movieId: int - id of the movie
            pred: list - list of ids of similar movies
        Returns:None
        """

        session = self.session
        movie = Movies(movieId=movieId, top1=pred[0], top2=pred[1], top3=pred[2], top4=pred[3],
        top5=pred[4], top6=pred[5], top7=pred[6], top8=pred[7], top9=pred[8], top10=pred[9])
        session.add(movie)
        session.commit()
        logger.info("Prediction of movie %s, added to database", movieId)

    def add_prediction_from_csv(self, file_name):
        """Add predictions to database from a csv file."""

        session = self.session

        try:
       
            data = self.__load_data(file_name) 

            for i in data:
                record = Predictions(**{
                    'movieId' : i[0],
                    'top1' : i[1],
                    'top2' : i[2],
                    'top3' : i[3],
                    'top4' : i[4],
                    'top5' : i[5],
                    'top6' : i[6],
                    'top7' : i[7],
                    'top8' : i[8],
                    'top9' : i[9],
                    'top10' : i[10]
                })
                session.add(record) #Add all the records

            session.commit() #Attempt to commit all the records
        except:
            session.rollback() #Rollback the changes on error
        finally:
            session.close() #Close the connection
        
        logger.info("Predictions from file {} are added to database".format(file_name))

