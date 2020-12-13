import json
import boto3
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth

def lambda_handler(event, context):
    query = event['queryStringParameters']['q']
    vpc_endpoint = 'vpc-photos-hw3-lr5lb46tdj7dbtfdeunl74joem.us-east-1.es.amazonaws.com'
    
    img_url_list = []
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
    lex_bot = boto3.client('lex-runtime', region_name='us-east-1')
    if query is not None:
        response = lex_bot.post_text(botName='photoChatBot', 
        botAlias = 'good', userId='10',
        inputText = query
        )
    x = response['slots']['X']
    y = response['slots']['Y']
    labels = []
    if x is not None:
        labels.append(x) 
    if y is not None:
        labels.append(y)
    
    for label in labels:
        res = es.search(index="photos-hw3",q=label)
        for img in res['hits']['hits']:
            bucket = img['_source']['bucket']
            image = img['_source']['objectKey']
            img_url = 'https://s3.amazonaws.com/'+ bucket + '/' + image 
            img_url_list.append(img_url)
    if labels:     
        return {   
			'statusCode': 200,
			'headers': {
				"Access-Control-Allow-Origin": "*",
				'Content-Type': 'application/json'
			}, 
			'body': json.dumps(img_url_list)
		}
    else:
	    return {
			'statusCode': 200,
			'x-api-key':'Rfmyt2P3271XedOHClrJbaEKhxi0zwqE16IFoiru',
			'headers': {
				"Access-Control-Allow-Origin": "*",
				'Content-Type': 'application/json'
			},
			'body': "Sorry! No images found with those keywords. "
		}