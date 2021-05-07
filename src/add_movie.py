import os
import logging

import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Column, Integer, String, Float, MetaData
from flask_sqlalchemy import SQLAlchemy


logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Base = declarative_base()

class Movies(Base):
	"""Create a data model for the database to be set up for capturing movies"""

	__tablename__ = 'movies'

	id = Column(Integer, primary_key=True)
	title = Column(String(100), unique=False, nullable=False)
	rating = Column(Float, unique=False, nullable=False)
	popularity = Column(Float, unique=False, nullable=False)
	cluster = Column(Integer, unique=False, nullable=False)
  	  
	def __repr__(self):
		return '<Movie %r>' % self.title


def create_db(engine_string: str) -> None:
    """Create database from provided engine string
    
    Args:
        engine_string: str - Engine string
    
    Returns: None
    """

    engine = sql.create_engine(engine_string) # set up mysql connection

    Base.metadata.create_all(engine) # create the movies table
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

    def add_movie(self, title: str, rating: float, popularity: int, cluster: int) -> None:
        """Seeds an existing database with additional movies.
        Args:
            title: str - Title of movie
            rating: float - Average rating of movie
            popularity: float - Popularity of movie
            cluster: int - Cluster number of movie
        Returns:None
        """

        session = self.session
        movie = Movies(title=title, rating=rating, popularity=popularity, cluster=cluster)
        session.add(movie)
        session.commit()
        logger.info("Movie %s, added to database", title)



