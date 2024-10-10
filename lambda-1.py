import json
import boto3

glue = boto3.client('glue')

def lambda_handler(event, context):
    response = glue.start_crawler(Name='serverless-glue-lambda-project-crawler')
    return {
        'statusCode': 200,
        'body': json.dumps('Crawler started successfully')
    }