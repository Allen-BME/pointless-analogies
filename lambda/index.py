import json
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3_client = boto3.client('s3')  # Create an S3 client
    bucket_name: str = os.environ['BUCKET_NAME']  # Get the bucket name from the environment
    s3_resource = boto3.resource('s3')  # Create an S3 resource
    bucket = s3_resource.Bucket(bucket_name)  # Set the bucket to the image bucket

# List for each image
    images = []
    for obj in bucket.objects.all():  # Create an image URL for each image in bucket
        images.append(f"https://{bucket_name}.s3.amazonaws.com/{obj.key}")

    body = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Pointless Analogies</title>
    </head>
    <body>
        <h1>Pointless Analogies</h1>
        <h2>Images in S3 Bucket</h2>
    '''
    # Log each image URL
    for image in images:
        print(image)

    # Add each image to the webpage
    for image in images:
        body += f"<img src='{image}' alt='S3 Image' style='width:300px;height:auto;'/><br>\n"

    body += '''
    </body>
    </html>
    '''

    response = {
        'statusCode': 200,
        'headers': {"Content-Type": "text/html",},
        'body': body
    }

    return response