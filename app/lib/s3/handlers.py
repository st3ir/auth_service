import logging

from botocore.exceptions import ClientError

from settings import s3_settings as s3_s
from lib.s3.client import s3_client


logger = logging.getLogger(__name__)


def get_object_from_s3(object_name: str) -> dict:
    bucket_name = s3_s.BUCKET_NAME
    logger.info('GET object [%s]:%s', bucket_name, object_name)
    try:
        return s3_client.get_object(Bucket=bucket_name, Key=object_name)
    except ClientError as e:
        logging.error(e, exc_info=True)
        raise e


def put_object_to_s3(object_name: str, data: bytes, url: str) -> None:
    bucket_name = s3_s.BUCKET_NAME
    logger.info('PUT object [%s]:%s', bucket_name, object_name)
    try:
        s3_client.put_object(Bucket=bucket_name, Key=url, Body=data)
    except ClientError as e:
        logging.error(e, exc_info=True)
        raise e


def remove_object_from_s3(object_name: str, url: str) -> None:
    bucket_name = s3_s.BUCKET_NAME
    logger.info('REMOVE object [%s]:%s', bucket_name, object_name)
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=url)
    except ClientError as e:
        logging.error(e, exc_info=True)
        raise e
