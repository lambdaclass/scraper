import logging
import os

import boto3
from botocore.exceptions import ClientError

from .notifications import slack_notification, Status

logger = logging.getLogger(__name__)


def backup_data():
    """Uploads scraped files to S3 bucket.
    Set bucket name in environment variable $S3_BUCKET
    """
    bucket_name = os.environ["S3_BUCKET"]

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)

    data_path = os.path.expanduser(os.environ["SCRAPER_DATA_PATH"])

    cboe_data = os.path.join(data_path, "cboe")
    cboe_folders = []
    if os.path.exists(cboe_data):
        cboe_folders = [
            os.path.join(cboe_data, folder) for folder in os.listdir(cboe_data)
        ]

    tiingo_data = os.path.join(data_path, "tiingo")
    tiingo_folders = []
    if os.path.exists(tiingo_data):
        tiingo_folders = [
            os.path.join(tiingo_data, folder)
            for folder in os.listdir(tiingo_data)
        ]

    done_cboe, fail_cboe = _upload_folders(bucket,
                                           "cboe",
                                           cboe_folders,
                                           remove_files=False)
    done_tiingo, fail_tiingo = _upload_folders(bucket,
                                               "tiingo",
                                               tiingo_folders,
                                               remove_files=True)

    done = done_cboe + done_tiingo
    failed = fail_cboe + fail_tiingo
    if len(done) > 0:
        msg = "Successful backup of symbols: " + ", ".join(done)
        slack_notification(msg, status=Status.Success)
    if len(failed) > 0:
        msg = "Unable to backup symbols: " + ", ".join(failed)
        slack_notification(msg, status=Status.Warning)


def _upload_folders(bucket, scraper, folders, remove_files=False):
    """Uploads folders to S3 bucket and (optionally) removes old files"""
    data_path = os.path.expanduser(os.environ["SCRAPER_DATA_PATH"])
    done, failed = [], []

    for folder in folders:
        symbol = os.path.basename(folder)
        try:
            if remove_files:
                _remove_old_files(bucket, prefix=scraper + "/" + symbol)
            _upload_folder(bucket, folder, data_path)
        except Exception:
            failed.append(os.path.basename(folder))
        else:
            done.append(os.path.basename(folder))

    return (done, failed)


def _upload_folder(bucket, folder, data_path):
    """Uploads folder contents to S3 bucket and *deletes* local files"""
    if not os.path.isdir(folder):
        return

    cleanup_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            key = os.path.relpath(file_path, data_path)
            if _key_exists(bucket, key):
                logger.debug("File already exists in S3")
                cleanup_files.append(file_path)
                continue
            try:
                bucket.upload_file(file_path, key)
            except Exception as e:
                msg = "Error uploading data file {} to S3.\nReceived exception message {}".format(
                    file_path, str(e))
                logger.error(msg, exc_info=True)
                slack_notification(msg)
                raise e
            else:
                logger.debug("Uploaded file %s to S3", file)
                cleanup_files.append(file_path)

    for file in cleanup_files:
        os.remove(file)


def _key_exists(bucket, key):
    try:
        bucket.Object(key).load()
    except ClientError as e:
        return int(e.response["Error"]["Code"]) != 404
    return True


def _remove_old_files(bucket, prefix):
    old_files = bucket.objects.filter(Prefix=prefix)
    for file in old_files:
        file.delete()
