import os
import json
import boto3
from urllib.parse import urlparse

def get_sm_client():
    session = boto3.session.Session()
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    return session.client(service_name='secretsmanager', region_name=region_name)

def get_s3_client():
    session = boto3.session.Session()
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    return session.client(service_name='s3', region_name=region_name)

def get_creds(client, secret_name='SECRET_NAME'):
    return json.loads(client.get_secret_value(SecretId=secret_name)['SecretString'])

def get_secret_key(name):
    try:
        secret_name = os.environ['SECRET_NAME']
        creds = get_creds(get_sm_client(), secret_name)
        return creds.get(name, 'No such secret value')
    except:
        print ('no such secret')
        return ""

def persist_to_s3(path, data):
    try:
        parsed_url = urlparse(path)
        s3_bucket = parsed_url.netloc
        s3_directory = parsed_url.path.lstrip('/')
        k = urlparse(path).path.split('/')[-1]
        s3_key = f"{s3_directory}recording.vtt" if not k else f"{s3_directory}.vtt"
        s3_client = get_s3_client()
        s3_client.put_object(Body=data, Bucket=s3_bucket, Key=s3_key)
        return s3_key
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)