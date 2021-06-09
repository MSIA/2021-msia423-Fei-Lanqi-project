#!/bin/bash
# run app when database is not set up but all data to be ingested is ready
# create db
python3 run.py create_db --engine_string=sqlite:///data/movies.db?charset=utf8mb4

# ingest movies and predictions (assuming data already generated from model pipeline)
python3 run.py ingest_to_movies --engine_string=sqlite:///data/movies.db?charset=utf8mb4 \
                            --file_path data/outputs/movies-feature.csv
python3 run.py ingest_to_predictions --engine_string=sqlite:///data/movies.db?charset=utf8mb4 \
                            --file_path models/predictions-predict.csv

# run the app using local sqlite db
python3 app.py