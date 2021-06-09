# Douban Movie Smart Finder
Project creator and Developer: Lanqi Fei

(QA contributions: Zixiao Huang)

## Table of Contents
<!-- toc -->
- [Project Charter](#project-charter)
  * [1. Vision](#1-vision)
  * [2. Mission](#2-mission)
  * [3. Success Criteria](#3-success-criteria)
- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)
  * [Workaround for potential Docker problem for Windows.](#workaround-for-potential-docker-problem-for-windows)

<!-- tocstop -->
## Project Charter

### 1. Vision
There are many recommender systems (RS) built for movies, such as [MovieLens](https://movielens.org/) and RS developed by OTT providers like Netflix. However, these recommender systems, especially those for personal use like MovieLens does not have a lot of Chinese movies available in their database, or movies from other Asian countries. In addition, since many Chinese people do not visit often or even have access to many foreign websites, using an RS built upon mainly data from non-Chinese people would generate biased result for Chinese users. This has made it hard for Chinese movie lovers to find similar movies they might like after watching some very interesting movie. Although they might try browsing through recommended movies on some Chinese OTT platforms like IQIYI, those are designed for specific platforms and will only recommend movies that are availale on that platform. Therefore, a movie finder designed specifically for Chinese people would be very helpful.

### 2. Mission
In this project, a movie finder is built to facilitate mainly Chinese people for finding similar movies that might interest them, using the most widely used movie platform in China - [Douban](http://douban.com/). The [original dataset](https://sites.google.com/site/erhengzhong/datasets) were collected for Erheng Zhong's research paper on KDD'12, TKDD'14, SDM'12 and its preprocessed version, which is used for this web application, can be found [here](https://github.com/SophonPlus/ChineseNlpCorpus/blob/master/datasets/ez_douban/intro.ipynb).

A user can type in the movie they like and the app will give the users a set of similar movies, ranked by similarity, movie rating or popularity, based on the user's choice. 

### 3. Success Criteria
1. Model Performance Metric
   * Average Satisfaction Score - Desired score prior to model deployment: > 3.8 
   
Explanation: the underlying algorithm is item-based collaborative filtering. To evaluate how successful it is, for each user, the model predicts a most similar movie to the user's best-rated movie. The satisfaction score for the user is defined as the user's rating of the most similar movie the model predicts, if it exists. Lastly, the average satisfaction score is calculated across all users.

The average rating for all movies in the database is around 3.8, and as a result, the app is considered successful if its satisfaction score is above the average rating.

2. Business Metric
To measure the business success of this app, standard A/B testing will be used, comparing the average ratings for movies made by users who did not consult the app and users who consulted this app for similar movies. A higher average rating for the second group of users would indicate a success in this app.
 
## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS, SASS, webfonts, image files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── run-pipeline.sh               <- Start up script for running model pipeline.
│   ├── run-tests.sh                  <- Start up script for running tests.
│   ├── Dockerfile                    <- Dockerfile for building image to run app 
│   ├── Dockerfile_python             <- Dockerfile for building image with python entrypoint
│   ├── Dockerfile_pipeline           <- Dockerfile for model pipeline.
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│   ├── modelconfig.yaml              <- Configurations for model pipeline
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── outputs/                      <- Model pipline outputs folder that *do not sync** to Github 
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│
├── references/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app
### 0. Environment Variables
Below are the list of environment variables that are used for this project:
- AWS Credentials
  + AWS_ACCESS_KEY_ID
  + AWS_SECRET_ACCESS_KEY
- Database Connection
  + SQLALCHEMY_DATABASE_URI *engine string of database*
- Database Connection (alternative)
  + MYSQL_HOST *database host*
  + MYSQL_PORT *database port*
  + MYSQL_USER *database user*
  + MYSQL_PASSWORD *database password*
  + MYSQL_DATABASE *database name*

### 1. Initialize the database 
#### Acquire the datasets and Upload to S3
The original dataset is found [here](https://github.com/SophonPlus/ChineseNlpCorpus/blob/master/datasets/ez_douban/intro.ipynb). Click the first link directs to the [download site](https://pan.baidu.com/s/1DkN1LmdSMzm_jCBKhbPbig) at Baidu Netdisk. Then it could be downloaded by clicking the download button (the second button near on the top right corner, which is next to the blue button). However, it requires one to have Baidu Netdisk installed and a Baidu account. To facilitate downloading, the raw datasets have already been included in this repo under `data/sample/`. 

To upload the raw datasets into the S3 bucket, run:

```bash
python run.py upload --local_path=<local_path> --s3_path=<s3_path> --data_file=<data_file>
```

By default, `python run.py upload` uploads `movies.csv` from `data/sample/` in this repo to `s3://2021-msia423-fei-lanqi/raw/`. To test the script, make sure to specify the argument `--s3_path` and change it to your S3 path. 

There are three data files used in this project, and so  `data_file` should be chosen from `movies.csv`, `links.csv` and `ratings.csv`

To write the datasets into S3 bucket in Docker:

- build a docker image:

At the root of the repository, run `docker build -f app/Dockerfile_python -t msia423 .`

- run the script:

```bash
docker run -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY msia423 run.py upload --local_path=<local_path> --s3_path=<s3_path> upload --data_file=<data_file>
```

#### Create the database 
To create the database in the location configured in `config.py`, run: 

```bash
python run.py create_db --engine_string=<engine_string>
```

By default, `python run.py create_db` creates a database at `sqlite:///data/movies.db` if MYSQL_HOST is not given.

To create the database using Docker, use the same image in the previous section:

```bash
docker run -it -e SQLALCHEMY_DATABASE_URI msia423 run.py create_db
```

Note that you have to mount the local data folder if you are creating a local database:

```bash
docker run --mount type=bind,source="$(pwd)/data",target=/app/data/ -e SQLALCHEMY_DATABASE_URI msia423 run.py create_db
```

#### Ingest data to database
To add data to movies table from a csv file to the database:

```bash
python run.py ingest_to_movies --engine_string=<engine_string> --file_path=<file_path>
```

The movies csv file should be the one generated from model pipeline, which will by default lie under `data/outputs/movies-feature.csv`.

Similarly, to add predictions from a csv to the databse:

```bash
python run.py ingest_to_predictions --engine_string=<engine_string> --file_path=<file_path>
```

The predictions csv file should be the one generated from model pipeline, which will by default lie under `models/predictions-predict.csv`. Note that by default only 10 similar movies are predicted for each movie, due to memory limit. This can be expanded but the schema of the database need to be modified.

To get movies and predictions data, please **do the step [Model Pipeline](#model-pipeline]) below before ingesting data**.

### 2. Model Pipeline

To run the model pipeline (acquire, clean, featurize, train, predict and evaluate), run the bash script:

```bash
./app/run-pipeline.sh
```

To run it in Docker, do:

```bash
docker build -f app/Dockerfile_sh -t msia423 . 
```

```bash
docker run --mount type=bind,source="$(pwd)/data",target=/app/data/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY msia423 app/run-model-pipeline.sh
```

### 4. Run the Flask app 

To run the Flask app locally, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

To run the app using Docker, do:

1. RDS or Local Database Ready

If you already have sqlite database with data ingested, or you want to use the RDS database, do:

```bash
 docker build -f app/Dockerfile -t msia423 .
```

```bash
docker run -e SQLALCHEMY_DATABASE_URI -p 5000:5000 --name test msia423
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

2. No Database Ready

If you don't have a database ready, but have the movies and predictions data ready to ingest to a local database, do:

```bash
 docker build -f app/Dockerfile_sh -t msia423 .
```

```bash
docker run -p 5000:5000 --name test msia423 app/run-app-pipeline.sh
```
 
If you do not have the data ready either, please **do the step [Model Pipeline](#model-pipeline]) below before ingesting data**.

#### Kill the container 

Once finished with the app, you will need to kill the container. To do so: 

```bash
docker kill test 
```

where `test` is the name given in the `docker run` command.

## Testing

From within the Docker container, the following command should work to run unit tests when run from the root of the repository: 

```bash
pytest
``` 

Using Docker, run the following, if the image has not been built yet:

```bash
 docker build -f app/Dockerfile_python -t msia423 .
```

To run the tests, run: 

```bash
 docker run msia423 -m pytest
```
 
