import argparse
import logging
import re
import requests

import pandas as pd
import boto3
import botocore


logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("aiobotocore").setLevel(logging.ERROR)
logging.getLogger("s3fs").setLevel(logging.ERROR)

logger = logging.getLogger('s3')

def download_from_source(local_path, file_name):
    url = "https://raw.githubusercontent.com/MSIA/2021-msia423-Fei-Lanqi-project/main/data/sample/" + file_name
    save_path = local_path + file_name
    response = requests.get(url)
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
        logger.info('Data downloaded from %s to %s', url, local_path)

def parse_s3(s3path):
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path

def upload_file_to_s3(local_path, s3path, file_name):
    s3bucket, s3_just_path = parse_s3(s3path+file_name)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--s3path', default='s3://2021-msia423-fei-lanqi/raw/',
                        help="s3 path to write data into")
    parser.add_argument('--local_path', default='data/',
                        help="local path to store or load data from")
    args = parser.parse_args()

    data_list = ["movies.csv", "links.csv", "ratings.csv"]

    for data_file in data_list:
        download_from_source(args.local_path, data_file)
        upload_file_to_s3(args.local_path, args.s3path, data_file)