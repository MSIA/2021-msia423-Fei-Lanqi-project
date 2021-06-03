#!/usr/bin/env bash

python3 run.py acquire
python3 run.py clean
python3 run.py featurize
python3 run.py train
python3 run.py predict
python3 run.py evaluate
