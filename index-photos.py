import json
import boto3
from datetime import datetime
import json
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth
 
def lambda_handler(event, context):
    vpc_endpoint = 'vpc-photos-hw3-lr5lb46tdj7dbtfdeunl74joem.us-east-1.es.amazonaws.com'
    
    rekognition_client = boto3.client('rekognition')
    
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_name = record['s3']['object']['key']
        img_size = record['s3']['object']['size']
        detected_labels = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            },
            MaxLabels=10
        )
        
    labels_list = []
    labels_object = detected_labels['Labels']
    for label in labels_object:
        labels_list.append(label["Name"])
        
    datetimeObject = datetime.now()
    createdTimestamp = datetimeObject.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    json_payload = {
                'objectKey': file_name,
                'bucket': bucket_name,
                'createdTimestamp': createdTimestamp,
                'labels': labels_list
            }
            
    region = 'us-east-1'
    service = 'es'

    credentials = boto3.Session().get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    token = credentials.token
      
    aws_auth = AWSRequestsAuth(aws_access_key=access_key,
                               aws_secret_access_key=secret_key,
                               aws_host=vpc_endpoint,
                               aws_token=token,
                               aws_region=region,
                               aws_service=service)
                               
    es = Elasticsearch(hosts = [{'host': vpc_endpoint, 'port': 443}],http_auth = aws_auth,use_ssl = True,verify_certs = True,connection_class = RequestsHttpConnection)
    
    es.index(index="photos-hw3", doc_type="_doc", id=createdTimestamp, body=json_payload)
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            'Content-Type': 'application/json'
        },
        'body': json.dumps('Image labels successfully generated!')
    }
