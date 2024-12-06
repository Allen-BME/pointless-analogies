import json
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3_client = boto3.client('s3')  # Create an S3 client
    
    html_bucket_name: str = os.environ['HTML_BUCKET_NAME']
    html_name: str = os.environ['HTML_FILE_NAME']
    
    s3_response = s3_client.get_object(
        Bucket = html_bucket_name,
        Key = html_name
    )
    html: str = s3_response['Body'].read().decode('utf-8') # s3_response['Body'] is a StreamingBody
    
    image_bucket_name: str = os.environ['IMAGE_BUCKET_NAME']  # Get the image bucket name from the environment
    image_s3_resource = boto3.resource('s3')  # Create an S3 resource
    image_bucket = image_s3_resource.Bucket(image_bucket_name)  # Set the bucket to the image bucket

    # List for each image
    images = []
    for obj in image_bucket.objects.all():  # Create an image URL for each image in bucket
        images.append(f"https://{image_bucket_name}.s3.amazonaws.com/{obj.key}")

    # Log each image URL
    for image in images:
        print(image)

    images_html = ""

    # Add each image to the webpage
    for image in images:
        images_html += f"<img src='{image}' alt='S3 Image' style='width:300px;height:auto;'/><br>\n"

    presigned_api_url = os.environ["PRESIGNED_API_URL"]

    # add images to html
    html = html.replace("{imagesBegin}", images_html)
    html = html.replace("{presignedUrlApi}", presigned_api_url)
    html = html.replace("{imageBucketName}", image_bucket_name)

    response = {
        'statusCode': 200,
        'headers': {"Content-Type": "text/html",},
        'body': html
    }

    return response