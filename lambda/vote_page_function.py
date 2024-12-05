import json
import boto3
import os

def lambda_handler(event, context):
    bucket_name: str = os.environ['HTML_BUCKET_NAME']
    html_name: str = os.environ['HTML_FILE_NAME']

    client = boto3.client('s3')
    html = client.get_object(
        Bucket = bucket_name,
        Key = html_name
    )

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": html['Body'].read(),
        "headers": {
            "content-type": "application.json"
        }
    }
    return response