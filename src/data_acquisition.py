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
    """
    Download the datasets from the github repo. This is not necessary if one already clones the repo.

    Args:
        local_path (str) - local path to save the downloaded datasets
        file_name (str) - the dataset name to download
    """

    url = "https://raw.githubusercontent.com/MSIA/2021-msia423-Fei-Lanqi-project/develop/data/sample/" + file_name # change develop branch to main when the branch is merged
    save_path = local_path + file_name
    response = requests.get(url)
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
        logger.info('Data %s downloaded from %s to %s', file_name, url, local_path)

def parse_s3(s3path):
    """
    Parse the input s3 path to get the bucket name

    Args:
        s3path (str) - s3 path

    Returns:
        s3bucket (str) - s3 bucket name
        s3path (str) - se path
    """

    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path

def upload_file_to_s3(local_path, s3path, file_name):
    """
    Upload the file in the local path to the given s3 path

    Args:
        local_path (str) - the local path which has the data
        s3path (str) - the s3 path which the data will be uploaded to
        file_name (str) - the name of the data file
    """
    s3bucket, s3_just_path = parse_s3(s3path+file_name)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path+file_name, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data %s uploaded from %s to %s', file_name, local_path, s3path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download and/or upload data to S3 bucket")
    parser.add_argument("--local_path", default='data/sample/',
                        help="local path to store and/or load from the raw datasets")
    parser.add_argument('--s3_path', default='s3://2021-msia423-fei-lanqi/raw/',
                        help="s3 path to write data into")

    subparsers = parser.add_subparsers(dest='subparser_name')
    sb_download = subparsers.add_parser("download", description="Download raw datasets")
    sb_upload = subparsers.add_parser("upload", description="Upload raw datasets to S3 bucket")
    sb_download_upload = subparsers.add_parser("download_upload", description="Download from source and upload raw datasets to S3")

    data_list = ["movies.csv", "links.csv", "ratings.csv"]

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'download':
        for data_file in data_list:
            download_from_source(args.local_path, data_file)
    elif sp_used == 'upload':
        for data_file in data_list:
            upload_file_to_s3(args.local_path, args.s3_path, data_file)
    elif sp_used == 'download_upload':
        for data_file in data_list:
            download_from_source(args.local_path, data_file)
            upload_file_to_s3(args.local_path, args.s3_path, data_file)
    else:
        parser.print_help()