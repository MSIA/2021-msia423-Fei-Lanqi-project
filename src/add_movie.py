"""Movie manager script."""

import logging

import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy
import pandas as pd


logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Base = declarative_base()

class Movies(Base):
    """Create a data model for the database to be set up for capturing movies."""

    __tablename__ = 'movies'

    movieId = Column(Integer, primary_key=True)
    doubanId = Column(Integer, unique=True, nullable=True)
    imdbId = Column(Integer, unique=True, nullable=True)
    title = Column(String(100), unique=False, nullable=True)
    rating = Column(Float, unique=False, nullable=False)
    popularity = Column(Integer, unique=False, nullable=False) # view counts

    def __repr__(self):
        """Rewrite representation string of a movie using id."""
        return '<Movie %r>' % self.title

class Predictions(Base):
    """Create a data model for the database for storing predictions."""

    __tablename__ = 'predictions'

    # top 10 most-similar movies to the movieId
    movieId = Column(Integer, primary_key=True)
    top1 = Column(Integer, unique=False, nullable=True)
    top2 = Column(Integer, unique=False, nullable=True)
    top3 = Column(Integer, unique=False, nullable=True)
    top4 = Column(Integer, unique=False, nullable=True)
    top5 = Column(Integer, unique=False, nullable=True)
    top6 = Column(Integer, unique=False, nullable=True)
    top7 = Column(Integer, unique=False, nullable=True)
    top8 = Column(Integer, unique=False, nullable=True)
    top9 = Column(Integer, unique=False, nullable=True)
    top10 = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        """Rewrite representation string of a prediction with a movie id."""
        return '<Prediction of %r>' % self.movieId

def create_db(engine_string: str) -> None:
    """Create database from provided engine string.

    Args:
        engine_string (str) - Engine string

    Returns: None
    """
    engine = sql.create_engine(engine_string) # set up mysql connection

    Base.metadata.create_all(engine) # create all tables

    logger.info("Database created.")

class MovieManager:
    """Manage database and faciliate data ingestion."""

    def __init__(self, app=None, engine_string=None):
        """
        Initialize the movie manager using app or engine string.

        Args:
            app: Flask - Flask app
            engine_string: str - Engine string

        Returns: None
        """
        # initialization
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
        """Close session.

        Returns: None
        """
        self.session.close()

    def validate_movie(self, record):
        """Validate a movie record.

        Args:
            record (dict) - dictionary of the record

        Returns:
            keep_record (bool) - whether to keep the record or discard it
            record (dict) - the updated record
        """
        keep_record = True # default

        # delete a record if movie id is null or non-int
        if not self.__validate_aux(record, 'movieId'):
            keep_record = False # return F because the whole record is deleted

        # delete douban id if it's null or non-int
        record = self.__validate_aux(record, 'doubanId')[1]

        # delete imdb id if it's null or non-int
        record = self.__validate_aux(record, 'imdbId')[1]

        # delete title id if it's null
        if record['title']=='nan':
            del record['title']
        else:
            record['title'] = str(record['title'])

        # check data type for rating
        record = self.__validate_aux_float(record, 'rating')[1]

        # replace missing popularity with 0
        try:
            record['popularity'] = int(record['popularity'])
        except ValueError:
            record['popularity'] = 0

        return keep_record, record

    @staticmethod
    def __validate_aux(record, element):
        """Auxilliary function for validating integer record.

        Args:
            record (dict) - the dictionary of record
            element (str) - the element to be validated in the dictionary

        Returns:
            valid (bool) - whether the element is valid
            record (dict) - the updated record
        """
        valid = False

        try:
            record[element] = int(record[element])
            valid = True
        except ValueError:
            del record[element]

        return valid, record

    @staticmethod
    def __validate_aux_float(record, element):
        """Auxilliary function for validating float record.

        Args:
            record (dict) - the dictionary of record
            element (str) - the element to be validated in the dictionary

        Returns:
            valid (bool) - whether the element is valid
            record (dict) - the updated record
        """
        valid = False

        try:
            record[element] = round(float(record[element]), 2)
            valid = True
        except ValueError:
            del record[element]

        return valid, record

    def add_movie(self, movie_id, douban_id, imdb_id, title, rating, popularity):
        """Seed an existing database with additional movies.

        Args:
            movieId (int) - Id of movie
            doubanId (int) - Douban id of movie
            imdbId (int) - IMDB id of movie
            title (str) - Title of movie
            rating (float) - Average rating of movie
            popularity (float) - Popularity of movie

        Returns: None
        """
        session = self.session
        record = {'movieId': movie_id, 'doubanId': douban_id, 'imdbId': imdb_id,
                'title': title, 'rating': rating, 'popularity': popularity}
        keep_record, record = self.validate_movie(record) # whether the record was kept or not

        if keep_record: # validate before insertion
            try:
                movie = Movies(**record)
                session.add(movie) # add a single movie
                session.commit()
                logger.debug("Movie %s, added to database", title)
            except SQLAlchemyError as error:
                session.rollback() # rollback the changes on error
                logger.error("Rollback due to an error: %s", str(error.__dict__['orig']))
        else:
            logger.debug("Invalid record encountered and dropped during ingestion")

    def add_movie_from_csv(self, file_path):
        """Add movies to database from a csv file."""
        try:
            data = pd.read_csv(file_path)
            logger.info("Movies data loaded.")
        except FileNotFoundError:
            logger.error("The movie data is not found in %s", file_path)

        # add all records in the file
        for i in range(data.shape[0]):
            # use add movie function
            self.add_movie(data.iloc[i,0], data.iloc[i,1], data.iloc[i,2],
                            data.iloc[i,3], data.iloc[i,4], data.iloc[i,5])

    def validate_prediction(self, record):
        """Validate a prediction record.

        Args:
            record (dict) - dictionary of the record

        Returns:
            keep_record (bool) - whether to keep the record or discard it
            record (dict) - the updated record
        """
        keep_record = True # default

        # delete a record if movie id is null or non-int
        if not self.__validate_aux(record, 'movieId'):
            keep_record = False # return F because the whole record is deleted

        # delete a record if any of its recommendation is null or non-int
        top1_valid, record = self.__validate_aux_float(record, 'top1')
        top2_valid, record = self.__validate_aux_float(record, 'top2')
        top3_valid, record = self.__validate_aux_float(record, 'top3')
        top4_valid, record = self.__validate_aux_float(record, 'top4')
        top5_valid, record = self.__validate_aux_float(record, 'top5')
        top6_valid, record = self.__validate_aux_float(record, 'top6')
        top7_valid, record = self.__validate_aux_float(record, 'top7')
        top8_valid, record = self.__validate_aux_float(record, 'top8')
        top9_valid, record = self.__validate_aux_float(record, 'top9')
        top10_valid, record = self.__validate_aux_float(record, 'top10')
        keep_record = keep_record and top1_valid and top2_valid and \
                    top3_valid and top4_valid and top5_valid and \
                    top6_valid and top7_valid and top8_valid and \
                    top9_valid and top10_valid

        return keep_record, record

    def add_prediction(self, movie_id, pred) -> None:
        """Seed an existing database with additional predictions.

        Args:
            movieId (int) - id of the movie
            pred (list) - list of ids of similar movies

        Returns:None
        """
        session = self.session
        record = {'movieId': movie_id, 'top1': pred[0], 'top2': pred[1],
            'top3': pred[2], 'top4': pred[3], 'top5': pred[4],
            'top6': pred[5], 'top7': pred[6], 'top8': pred[7],
            'top9': pred[8], 'top10': pred[9]}
        keep_record, record = self.validate_prediction(record)

        if keep_record: # validate before insertion
            try:
                prediction = Predictions(**record)
                session.add(prediction) # add a single prediction
                session.commit()
                logger.debug("Prediction of movie %d, added to database", movie_id)
            except SQLAlchemyError as error:
                session.rollback() # rollback the changes on error
                logger.error("Rollback due to an error: %s", str(error.__dict__['orig']))
        else:
            logger.debug("Invalid record encountered and dropped during ingestion")

    def add_prediction_from_csv(self, file_path):
        """Add predictions to database from a csv file."""
        try:
            data = pd.read_csv(file_path)
            logger.info("Predictions data loaded.")
        except FileNotFoundError:
            logger.error("The prediction data is not found in %s", file_path)

        # add all records in the file
        for i in range(data.shape[0]):
            # use add prediction function
            pred = [data.iloc[i,1], data.iloc[i,2], data.iloc[i,3], data.iloc[i,4],
                    data.iloc[i,5], data.iloc[i,6], data.iloc[i,7], data.iloc[i,8],
                    data.iloc[i,9], data.iloc[i,10]]
            self.add_prediction(data.iloc[i,0], pred)
