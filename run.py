import argparse

import logging.config
logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('douban-rs-pipeline')

from src.add_movie import MovieManager, create_db
from src.data_acquisition import upload_file_to_s3
import src.acquire as acquire
import src.clean as clean
import src.featurize as featurize
import src.train as train
import src.predict as predict
import src.evaluate as evaluate
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

import yaml
import pandas as pd
import numpy as np

if __name__ == '__main__':

    # Add parsers for both creating a database and adding movies to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')


    # UPLOAD DATA TO S3
    sb_upload = subparsers.add_parser("upload", description="Upload raw datasets to S3 bucket")
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
    sb_ingest_movies = subparsers.add_parser("ingest_to_movies", description="Add data to movies table")
    sb_ingest_movies.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sb_ingest_movies.add_argument("--file_path", default="data/outputs/movies-feature.csv", 
    help="Path of the csv file")

    sb_ingest_pred = subparsers.add_parser("ingest_to_predictions", description="Add data to predictions table")
    sb_ingest_pred.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sb_ingest_pred.add_argument("--file_path", default="data/outputs/predictions-predict.csv", 
    help="Path of the csv file")

    # MODEL PIPELINE
    # Sub-parser for acquiring data
    sb_acquire = subparsers.add_parser("acquire", description="Acquire data from S3")
    sb_acquire.add_argument("--config", default="config/modelconfig.yaml", help="Model configuration file")
    sb_acquire.add_argument("--output_movies", default="data/outputs/movies-raw.csv", 
    help="Path to save raw movies data")
    sb_acquire.add_argument("--output_links", default="data/outputs/links-raw.csv", 
    help="Path to save raw links data")
    sb_acquire.add_argument("--output_ratings", default="data/outputs/ratings-raw.csv", 
    help="Path to save raw ratings data")

    # Sub-parser for cleaning data
    sb_clean = subparsers.add_parser("clean", description="Clean raw data")
    sb_clean.add_argument("--config", default="config/modelconfig.yaml", help="Model configuration file")
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
    sb_featurize.add_argument("--config", default="config/modelconfig.yaml", 
    help="Model configuration file")
    sb_featurize.add_argument("--input_movies", default="data/outputs/movies-clean.csv", 
    help="Path to load cleanaed movies data")
    sb_featurize.add_argument("--input_ratings", default="data/outputs/ratings-clean.csv", 
    help="Path to load cleaned ratings data")
    sb_featurize.add_argument("--output_movies", default="data/outputs/movies-feature.csv", 
    help="Path to save featurized and merged movies data")
    sb_featurize.add_argument("--output_ratings", default="data/outputs/ratings-feature.csv", 
    help="Path to save featurized ratings data")

    # Sub-parser for training model
    sb_train = subparsers.add_parser("train", description="Training model")
    sb_train.add_argument("--input_ratings", default="data/outputs/ratings-clean.csv", 
    help="Path to load cleaned ratings data")
    sb_train.add_argument("--output_ratings_pivot", default="model/ratings-pivot-train.csv", 
    help="Path to ratings matrix")
    sb_train.add_argument("--output_movie_id", default="model/movieID-train.npy", 
    help="Path to save movie IDs array")
    sb_train.add_argument("--output_user_id", default="model/userID-train.npy", 
    help="Path to save user IDs array")
    sb_train.add_argument("--output_corr", default="model/corr-train.npy", 
    help="Path to save trained distance matrix")

    # Sub-parser for generating predictions
    sb_predict = subparsers.add_parser("predict", description="Generate predictions")
    sb_predict.add_argument("--config", default="config/modelconfig.yaml", 
    help="Model configuration file")
    sb_predict.add_argument("--input_movie_id", default="model/movieID-train.npy", 
    help="Path to load movieID array")
    sb_predict.add_argument("--input_corr", default="model/corr-train.npy", 
    help="Path to load distance matrix")
    sb_predict.add_argument("--output_predictions", default="model/predictions-predict.csv", 
    help="Path to save predictions")

    # Sub-parser for evaluating model
    sb_evaluate = subparsers.add_parser("evaluate", description="Evaluate model performance")
    sb_evaluate.add_argument("--input_ratings_pivot", default="model/ratings-pivot-train.csv", 
    help="Path to load ratings matrix")
    sb_evaluate.add_argument("--input_user_id", default="model/userID-train.npy", 
    help="Path to load userID array")
    sb_evaluate.add_argument("--input_movie_id", default="model/movieID-train.npy", 
    help="Path to load movieID array")
    sb_evaluate.add_argument("--input_corr", default="model/corr-train.npy", 
    help="Path to load distance matrix")
    sb_evaluate.add_argument("--output", default="data/outputs/score-evaluate.txt", 
    help="Path to save the satisfaction score")

    args = parser.parse_args()
    sp_used = args.subparser_name

    data_list = ["movies.csv", "links.csv", "ratings.csv"]

    if sp_used == 'upload':
        for data_file in data_list:
            upload_file_to_s3(args.local_path, args.s3_path, data_file)
    elif sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest_to_movies':
        mm = MovieManager(engine_string=args.engine_string)
        mm.add_movie_from_csv(args.file_path)
        mm.close()
    elif sp_used == 'ingest_to_predictions':
        mm = MovieManager(engine_string=args.engine_string)
        mm.add_prediction_from_csv(args.file_path)
        mm.close()
    elif sp_used == 'acquire':
        with open(args.config, "r") as f: # Load configuration file for parameters and tmo path
            config = yaml.load(f, Loader=yaml.FullLoader)
        movies, links, ratings = acquire.acquire(**config['acquire']['acquire'])
        movies.to_csv(args.output_movies, index=False)
        links.to_csv(args.output_links, index=False)
        ratings.to_csv(args.output_ratings, index=False)
        logger.info('Raw data saved to the given paths')
    elif sp_used == 'clean':
        with open(args.config, "r") as f: # Load configuration file for parameters and tmo path
            config = yaml.load(f, Loader=yaml.FullLoader)
        movies = pd.read_csv(args.input_movies); links = pd.read_csv(args.input_links)
        ratings = pd.read_csv(args.input_ratings)
        logger.info('Raw data loaded from the given paths')
        movies, ratings = clean.clean(movies, links, ratings, config['clean'])
        movies.to_csv(args.output_movies, index=False); ratings.to_csv(args.output_ratings, index=False)
        logger.info("Cleaned data saved to the given paths")
    elif sp_used == 'featurize':
        with open(args.config, "r") as f: # Load configuration file for parameters and tmo path
            config = yaml.load(f, Loader=yaml.FullLoader)
        movies = pd.read_csv(args.input_movies); ratings = pd.read_csv(args.input_ratings)
        logger.info('Cleaned data loaded from the given paths')
        movies, ratings = featurize.featurize(movies, ratings, **config['featurize']['featurize'])
        movies.to_csv(args.output_movies, index=False); ratings.to_csv(args.output_ratings, index=False)
        logger.info("Featurized data saved to the given paths")
    elif sp_used == 'train':
        ratings = pd.read_csv(args.input_ratings); logger.info('Featurized data loaded from the given paths')
        ratings_pivot, movieID, userID, corr = train.train(ratings)
        ratings_pivot.to_csv(args.output_ratings_pivot, index=False)
        np.save(args.output_movie_id, movieID); np.save(args.output_user_id, userID)
        np.save(args.output_corr, corr)
        logger.info("Model outputs saved to the given paths")
    elif sp_used == 'predict':
        with open(args.config, "r") as f: # Load configuration file for parameters and tmo path
            config = yaml.load(f, Loader=yaml.FullLoader)
        corr = np.load(args.input_corr); movieID = np.load(args.input_movie_id)
        logger.info('Trained objects loaded from the given paths')
        predictions = predict.predict(corr, movieID, config['predict'])
        predictions.to_csv(args.output_predictions, index=False)
        logger.info("Predictions saved to the given paths")
    elif sp_used == 'evaluate':
        ratings_pivot = pd.read_csv(args.input_ratings_pivot)
        corr = np.load(args.input_corr)
        movieID = np.load(args.input_movie_id)
        userID = np.load(args.input_user_id)
        logger.info('Inputs loaded from the given paths')
        result = evaluate.evaluate(ratings_pivot, movieID, userID, corr)
        with open(args.output, 'w') as f:
            f.write("Average satisfaction score %.2f: " % result)
        logger.info("Evaluation score saved to the given path")
    else:
        parser.print_help()
