import argparse

import logging.config
logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('douban-rs-pipeline')

from src.add_movie import MovieManager, create_db
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--title", default="芳华", help="Title of movie to be added")
    sb_ingest.add_argument("--rating", default=4.5, help="Average rating of movie to be added")
    sb_ingest.add_argument("--popularity", default=1000, help="Popularity of movie to be added")
    sb_ingest.add_argument("--cluster", default=1, help="Cluster of movie to be added")
    sb_ingest.add_argument("--engine_string", default='sqlite:///data/movies.db',
                           help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        tm = TrackManager(engine_string=args.engine_string)
        tm.add_movie(args.title, args.rating, args.popularity, args.cluster)
        tm.close()
    else:
        parser.print_help()
