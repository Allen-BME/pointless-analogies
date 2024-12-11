import json
import boto3
import os
from botocore.exceptions import ClientError

def main_page_function(event, context):
    # Get image bucket name
    image_bucket_name: str = os.environ['IMAGE_BUCKET_NAME']
    # Create a new S3 client to access buckets
    client = boto3.client('s3')

    # Get table name
    table_name: str = os.environ['TABLE_NAME']
    # Get an object representing the table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Get HTML names
    html_bucket_name: str = os.environ['HTML_BUCKET_NAME']
    html_file_name: str = os.environ['HTML_FILE_NAME']
    html_snippet_name: str = os.environ['HTML_SNIPPET_NAME']

    # Get API Endpoint
    api_endpoint: str = os.environ['API_ENDPOINT']

    # Get the html page stored in the bucket under html_file_name
    s3_response = client.get_object(
        Bucket = html_bucket_name,
        Key = html_file_name
    )
    main_page: str = s3_response['Body'].read().decode('utf-8')
    
    # Get the html snippet stored in the bucket under html_snippet_name
    s3_response = client.get_object(
        Bucket = html_bucket_name,
        Key = html_snippet_name
    )
    image_snippet: str = s3_response['Body'].read().decode('utf-8')

    # Replace {apiEndpoint} in the html snippet with the actual endpoint
    image_snippet = image_snippet.replace("{apiEndpoint}", f'{api_endpoint}/vote')

    # Get all items from the table
    response = table.scan()
    items = response.get('Items', [])

    for item in items:
        # Replace ImageHash in a snippet copy with the actual image hash
        image_hash = item['ImageHash']
        image_snippet_copy = image_snippet.replace("{ImageHash}", image_hash)

        # Put the S3 image into the image snippet copy
        image_url = f"https://{image_bucket_name}.s3.amazonaws.com/{image_hash}"
        image_snippet_copy = image_snippet_copy.replace("{image}", image_url)
        print(image_snippet_copy)

        # Put the current copy in at {imagesBegin}
        main_page = main_page.replace("{imagesBegin}", image_snippet_copy)
    main_page = main_page.replace("{imagesBegin}", "")

    # replace variables in main page html
    main_page = main_page.replace("{presignedUrlApi}", api_endpoint)
    main_page = main_page.replace("{imageBucketName}", image_bucket_name)

    # Give the modified main page html to the user
    function_response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": main_page.encode('utf-8'),
        "headers": {
            "content-type": "text/html"
        }
    }
    return function_response