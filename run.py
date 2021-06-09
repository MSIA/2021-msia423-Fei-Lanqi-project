"""
The orchestration script.
"""

import argparse
import logging.config
# logging has to be configured here to show loggers from other modules
logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('douban-rs-pipeline')

import yaml
import pandas as pd
import numpy as np

from src.add_movie import MovieManager, create_db
from src.data_acquisition import upload_file_to_s3
import src.acquire as acquire
import src.clean as clean
import src.featurize as featurize
import src.train as train
import src.predict as predict
import src.evaluate as evaluate
from config.flaskconfig import SQLALCHEMY_DATABASE_URI



if __name__ == '__main__':

    # Add parsers for both creating a database and adding movies to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    parser.add_argument('--config', default=None, help='Path to configuration file')

    subparsers = parser.add_subparsers(dest='subparser_name')

    # UPLOAD DATA TO S3
    sb_upload = subparsers.add_parser("upload", description="Upload raw datasets to S3 bucket")
    sb_upload.add_argument("--data_file", default='movies.csv',
                        choices=['movies.csv', 'links.csv', 'ratings.csv'], help="dataset name")
    sb_upload.add_argument("--local_path", default='data/sample/',
                        help="local path to store and/or load from the raw datasets")
    sb_upload.add_argument('--s3_path', default='s3://2021-msia423-fei-lanqi/raw/',
                        help="s3 path to write data into")

    # CREATE DATABASE
    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                        help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting movies / predictions table
    sb_ingest_movies = subparsers.add_parser("ingest_to_movies",
                        description="Add data to movies table")
    sb_ingest_movies.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                        help="SQLAlchemy connection URI for database")
    sb_ingest_movies.add_argument("--file_path", default="data/outputs/movies-feature.csv",
                        help="Path of the csv file")

    sb_ingest_pred = subparsers.add_parser("ingest_to_predictions",
                        description="Add data to predictions table")
    sb_ingest_pred.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
    help="SQLAlchemy connection URI for database")
    sb_ingest_pred.add_argument("--file_path", default="models/predictions-predict.csv",
    help="Path of the csv file")

    # MODEL PIPELINE
    # Sub-parser for acquiring data
    sb_acquire = subparsers.add_parser("acquire", description="Acquire data from S3")
    sb_acquire.add_argument("--output_movies", default="data/outputs/movies-raw.csv",
                        help="Path to save raw movies data")
    sb_acquire.add_argument("--output_links", default="data/outputs/links-raw.csv",
                        help="Path to save raw links data")
    sb_acquire.add_argument("--output_ratings", default="data/outputs/ratings-raw.csv",
                        help="Path to save raw ratings data")

    # Sub-parser for cleaning data
    sb_clean = subparsers.add_parser("clean", description="Clean raw data")
    sb_clean.add_argument("--config", default="config/modelconfig.yaml",
                        help="Model configuration file")
    sb_clean.add_argument("--input_movies", default="data/outputs/movies-raw.csv",
                        help="Path to load raw movies data")
    sb_clean.add_argument("--input_links", default="data/outputs/links-raw.csv",
                        help="Path to load raw links data")
    sb_clean.add_argument("--input_ratings", default="data/outputs/ratings-raw.csv",
                        help="Path to load raw ratings data")
    sb_clean.add_argument("--output_movies", default="data/outputs/movies-clean.csv",
                        help="Path to save cleaned and merged movies data")
    sb_clean.add_argument("--output_ratings", default="data/outputs/ratings-clean.csv",
                        help="Path to save cleaned ratings data")

    # Sub-parser for featurizing data
    sb_featurize = subparsers.add_parser("featurize", description="Featurize cleaned data")
    sb_featurize.add_argument("--input_movies", default="data/outputs/movies-clean.csv",
                        help="Path to load cleanaed movies data")
    sb_featurize.add_argument("--input_ratings", default="data/outputs/ratings-clean.csv",
                        help="Path to load cleaned ratings data")
    sb_featurize.add_argument("--output_movies", default="data/outputs/movies-feature.csv",
                        help="Path to save featurized ratings data")

    # Sub-parser for training model
    sb_train = subparsers.add_parser("train", description="Training model")
    sb_train.add_argument("--input_ratings", default="data/outputs/ratings-clean.csv",
                        help="Path to load cleaned ratings data")
    sb_train.add_argument("--output_ratings_pivot", default="models/ratings-pivot-train.csv",
                        help="Path to ratings matrix")
    sb_train.add_argument("--output_movie_id", default="models/movieID-train.npy",
    help="Path to save movie IDs array")
    sb_train.add_argument("--output_user_id", default="models/userID-train.npy",
                        help="Path to save user IDs array")
    sb_train.add_argument("--output_corr", default="models/corr-train.npy",
                        help="Path to save trained distance matrix")

    # Sub-parser for generating predictions
    sb_predict = subparsers.add_parser("predict", description="Generate predictions")
    sb_predict.add_argument("--input_movie_id", default="models/movieID-train.npy",
                        help="Path to load movieID array")
    sb_predict.add_argument("--input_corr", default="models/corr-train.npy",
                        help="Path to load distance matrix")
    sb_predict.add_argument("--output_predictions", default="models/predictions-predict.csv",
                        help="Path to save predictions")

    # Sub-parser for evaluating model
    sb_evaluate = subparsers.add_parser("evaluate", description="Evaluate model performance")
    sb_evaluate.add_argument("--input_ratings_pivot", default="models/ratings-pivot-train.csv",
                        help="Path to load ratings matrix")
    sb_evaluate.add_argument("--input_user_id", default="models/userID-train.npy",
                        help="Path to load userID array")
    sb_evaluate.add_argument("--input_movie_id", default="models/movieID-train.npy",
                        help="Path to load movieID array")
    sb_evaluate.add_argument("--input_corr", default="models/corr-train.npy",
                        help="Path to load distance matrix")
    sb_evaluate.add_argument("--output", default="data/outputs/score-evaluate.txt",
                        help="Path to save the satisfaction score")

    args = parser.parse_args()
    sp_used = args.subparser_name

    # Load configuration file for parameters and tmo path
    if args.config is not None:
        try:
            with open(args.config, "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            logger.error("Configuration file not found in %s", args.config)
    if sp_used == 'upload': # upload to s3
        upload_file_to_s3(args.local_path, args.s3_path, args.data_file)
    elif sp_used == 'create_db': # create database
        create_db(args.engine_string)
    elif sp_used == 'ingest_to_movies': # movies data ingestion
        mm = MovieManager(engine_string=args.engine_string)
        mm.add_movie_from_csv(args.file_path)
        mm.close()
    elif sp_used == 'ingest_to_predictions': # predictions data ingestion
        mm = MovieManager(engine_string=args.engine_string)
        mm.add_prediction_from_csv(args.file_path)
        mm.close()
    elif sp_used == 'acquire': # model pipeline data acquisition
        movies, links, ratings = acquire.acquire(**config['acquire']['acquire'])

        try:
            movies.to_csv(args.output_movies, index=False)
            links.to_csv(args.output_links, index=False)
            ratings.to_csv(args.output_ratings, index=False)
            logger.info('Raw data saved to the given paths')
        except IOError:
            logger.error("Cannot write to files")
    elif sp_used == 'clean': # data cleaning
        try:
            movies = pd.read_csv(args.input_movies)
            links = pd.read_csv(args.input_links)
            ratings = pd.read_csv(args.input_ratings)
            logger.info('Raw data loaded from the given paths')
        except FileNotFoundError:
            logger.error("Clean input files not found")

        movies, ratings = clean.clean(movies, links, ratings, config['clean'])

        try:
            movies.to_csv(args.output_movies, index=False)
            ratings.to_csv(args.output_ratings, index=False)
            logger.info("Cleaned data saved to the given paths")
        except IOError:
            logger.error("Cannot write to files")
    elif sp_used == 'featurize': # feature engineering
        try:
            movies = pd.read_csv(args.input_movies)
            ratings = pd.read_csv(args.input_ratings)
            logger.info('Cleaned data loaded from the given paths')
        except FileNotFoundError:
            logger.error("Featurize input files not found")

        movies = featurize.featurize(movies, ratings, **config['featurize']['featurize'])

        try:
            movies.to_csv(args.output_movies, index=False)
            logger.info("Featurized data saved to the given paths")
        except IOError:
            logger.error("Cannot write to file %s", args.output_movies)
    elif sp_used == 'train': # model training
        try:
            ratings = pd.read_csv(args.input_ratings)
            logger.info('Featurized data loaded from the given path %s', args.input_ratings)
        except FileNotFoundError:
            logger.error("Train input file not found")

        ratings_pivot, movieID, userID, corr = train.train(ratings)
        ratings_pivot.to_csv(args.output_ratings_pivot, index=False)

        try:
            np.save(args.output_movie_id, movieID)
            np.save(args.output_user_id, userID)
            np.save(args.output_corr, corr)
            logger.info("Model outputs saved to the given paths")
        except IOError:
            logger.error("Cannot write to files")
    elif sp_used == 'predict': # predict
        try:
            corr = np.load(args.input_corr)
            movieID = np.load(args.input_movie_id)
            logger.info('Trained objects loaded from the given paths')
        except FileNotFoundError:
            logger.error('Trained objects not found in the given paths')

        predictions = predict.predict(corr, movieID, config['predict'])

        try:
            predictions.to_csv(args.output_predictions, index=False)
            logger.info("Predictions saved to the given paths")
        except IOError:
            logger.error("Cannot write to file %s", args.output_predictions)
    elif sp_used == 'evaluate': # model evaluation
        try:
            ratings_pivot = pd.read_csv(args.input_ratings_pivot)
            corr = np.load(args.input_corr)
            movie_id = np.load(args.input_movie_id)
            user_id = np.load(args.input_user_id)
            logger.info('Inputs loaded from the given paths')
        except FileNotFoundError:
            logger.error('Inputs not found in the given paths')

        result = evaluate.evaluate(ratings_pivot, movie_id, user_id, corr)

        try:
            with open(args.output, 'w') as f:
                f.write("Average satisfaction score %.2f: " % result)
            logger.info("Evaluation score saved to the given path")
        except IOError:
            logger.error("Cannot write to file %s", args.output)
    else:
        parser.print_help()
