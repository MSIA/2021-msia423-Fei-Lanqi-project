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
### 1. Initialize the database 
#### Acquire the datasets
The original dataset is found [here](https://github.com/SophonPlus/ChineseNlpCorpus/blob/master/datasets/ez_douban/intro.ipynb). Click the first link directs to the [download site](https://pan.baidu.com/s/1DkN1LmdSMzm_jCBKhbPbig) at Baidu Netdisk. Then it could be downloaded by clicking the download button (the second button near on the top right corner, which is next to the blue button). However, it requires one to have Baidu Netdisk installed and a Baidu account. To facilitate downloading, the raw datasets have already been included in this repo under `data/sample/`. They could also be downloaded via the `src/data_acquisition.py` described below.

To download the raw datasets and write them into the S3 bucket, run:

```bash
python src/data_acquisition.py --local_path=<local_path> --s3_path=<s3_path> download_upload
```

By default, `python src/data_acquisition.py download_upload` downloads the three raw datasets from `data/sample/` in this repo to local path `data/sample/` and uploads them to `s3://2021-msia423-fei-lanqi/raw/`. To test the script, make sure to specify the argument `--s3_path` and change it to your S3 path. Also note that the arguments have to be provided before the subparser `ownload_upload`. One could also use the subparser `download` or `upload` to only download the datasets from source or only upload the datasets to S3.

To write the datasets into S3 bucket in Docker:

Note that since we are building the image from inside the repo, where the raw datasets already exist, there is no need to download the datasets again.

- build a docker image:

Inside the repository, run `docker build -f app/Dockerfile_python -t msia423 .`

- run the script:

```bash
docker run -it --env AWS_ACCESS_KEY_ID --env AWS_SECRET_ACCESS_KEY msia423 src/data_acquisition.py --s3_path=<s3_path> upload
```

- check the data is uploaded to s3:

```bash
aws s3 ls <s3_path>
```

#### Create the database 
To create the database in the location configured in `config.py`, run: 

```bash
python run.py create_db --engine_string=<engine_string>
```

By default, `python run.py create_db` creates a database at `sqlite:///data/movies.db` if MYSQL_HOST is not given.

To create the database using Docker, run:
- build a docker image:

Inside the repository, run `docker build -f app/Dockerfile_python -t msia423 .`

- create the database in the RDS for this project:

```bash
docker run -it --env MYSQL_HOST --env MYSQL_PORT --env MYSQL_USER --env MYSQL_PASSWORD --env MYSQL_DATABASE msia423 run.py create_db
```

To only access and look into the database:
`docker run -it --rm mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}`, then you can run `SHOW DATABASES;` -> `USE msia423;` -> `SHOW TABLES;`->`DESCRIBE movies;` to check the schema.

#### Adding movies 
To add data to movies table from a csv file to the database:

```bash
python run.py ingest_to_movies --engine_string=<engine_string> --file_path=<file_path>
```

The movies csv file should be the one generated from model pipeline, which will by default lie under `data/outputs/movies-feature.csv`.

Similarly, to add predictions from a csv to the databse:

```bash
python run.py ingest_to_predictions --engine_string=<engine_string> --file_path=<file_path>
```

The predictions csv file should be the one generated from model pipeline, which will by default lie under `data/outputs/predictions-predict.csv`. Note that by default only 10 similar movies are predicted for each movie, due to memory limit. This can be expanded but the schema of the database need to be modified.

To get movies and predictions data, please **do the step [Model Pipeline](#model-pipeline]) below before building ingesting data**.

### 2. Model Pipeline

To run the model pipeline (acquire, clean, featurize, train, predict and evaluate), run the bash script:

```bash
./app/run-pipeline.sh
```

To run it in Docker, do:

```bash
docker build -f app/Dockerfile_pipeline -t douban-pipeline . 
```

```bash
docker run --mount type=bind,source="$(pwd)/data",target=/app/data/ douban-pipeline --env AWS_ACCESS_KEY_ID --env AWS_SECRET_ACCESS_KEY app/run-pipeline.sh
```

### 4. Run the Flask app 

To run the Flask app locally, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

#### Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/movies.db'  # URI (engine string) for database that contains tracks
APP_NAME = "douban-rs"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

To run the app using Docker, do:

1. Build the image 

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t msia423 .
```

This command builds the Docker image, with the tag `msia423`, based on the instructions in `app/Dockerfile` and the files existing in this directory.
 
2. Run the container 

To run the app, run from this directory: 

```bash
docker run -p 5000:5000 --name test msia423
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

This command runs the `msia423` image as a container named `test` and forwards the port 5000 from container to your laptop so that you can access the flask app exposed through that port. 

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `app/Dockerfile`)

(Note that you should provide necessary environment variables since the app will need to access the RDS tables, otherwise, you'll need to set up your local database ready with movies and predictions ingested, see [Initialize the database](#initialize-the-database))

3. Kill the container 

Once finished with the app, you will need to kill the container. To do so: 

```bash
docker kill test 
```

where `test` is the name given in the `docker run` command.

## Testing

From within the Docker container, the following command should work to run unit tests when run from the root of the repository: 

```bash
python -m pytest
``` 

Using Docker, run the following, if the image has not been built yet:

```bash
 docker build -f app/Dockerfile_python -t douban-rs .
```

To run the tests, run: 

```bash
 docker run douban-rs -m pytest
```
 
