import os
import json
import boto3

def get_sm_client():
    session = boto3.session.Session()
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    return session.client(service_name='secretsmanager', region_name=region_name)

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
