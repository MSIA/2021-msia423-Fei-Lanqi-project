#!/usr/bin/env bash

# acquire raw data from S3
python3 run.py --config=config/modelconfig.yaml acquire --output_movies=data/outputs/movies-raw.csv \
        --output_links=data/outputs/links-raw.csv --output_ratings=data/outputs/ratings-raw.csv

# clean raw data
python3 run.py --config=config/modelconfig.yaml clean --input_movies=data/outputs/movies-raw.csv \
        --input_links=data/outputs/links-raw.csv --input_ratings=data/outputs/ratings-raw.csv \
        --output_movies=data/outputs/movies-clean.csv --output_ratings=data/outputs/ratings-clean.csv

# feature engineering
python3 run.py --config=config/modelconfig.yaml featurize --input_movies=data/outputs/movies-clean.csv \
        --input_ratings=data/outputs/ratings-clean.csv --output_movies=data/outputs/movies-feature.csv

# model training
python3 run.py --config=config/modelconfig.yaml train --input_ratings=data/outputs/ratings-clean.csv \
        --output_ratings_pivot=data/outputs/ratings-pivot-train.csv \
        --output_movie_id=data/outputs/movieID-train.npy --output_user_id=data/outputs/userID-train.npy \
        --output_corr=data/outputs/corr-train.npy

# generate predictions
python3 run.py --config=config/modelconfig.yaml predict --input_movie_id=data/outputs/movieID-train.npy \
        --input_corr=data/outputs/corr-train.npy \
        --output_predictions=data/outputs/predictions-predict.csv

# model evaluation
python3 run.py --config=config/modelconfig.yaml evaluate \
        --input_ratings_pivot=data/outputs/ratings-pivot-train.csv --input_corr=data/outputs/corr-train.npy \
        --input_user_id=data/outputs/userID-train.npy --input_movie_id=data/outputs/movieID-train.npy \
        --output=data/outputs/score-evaluate.txt

