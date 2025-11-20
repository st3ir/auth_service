import boto3

from settings import s3_settings as s3_s

session = boto3.Session()
s3_client = session.client(
    service_name='s3',
    endpoint_url=s3_s.BUCKET_URL,
    aws_access_key_id=s3_s.BUCKET_ACCESS_KEY,
    aws_secret_access_key=s3_s.BUCKET_SECRET_KEY,
    region_name=s3_s.BUCKET_REGION
)
