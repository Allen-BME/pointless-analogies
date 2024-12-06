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

# def lambda_handler(event, context):
#     s3_client = boto3.client('s3')  # Create an S3 client
    
#     html_bucket_name: str = os.environ['HTML_BUCKET_NAME']
#     html_name: str = os.environ['HTML_FILE_NAME']
    
#     s3_response = s3_client.get_object(
#         Bucket = html_bucket_name,
#         Key = html_name
#     )
#     html: str = s3_response['Body'].read().decode('utf-8') # s3_response['Body'] is a StreamingBody
    
#     image_bucket_name: str = os.environ['IMAGE_BUCKET_NAME']  # Get the image bucket name from the environment
#     image_s3_resource = boto3.resource('s3')  # Create an S3 resource
#     image_bucket = image_s3_resource.Bucket(image_bucket_name)  # Set the bucket to the image bucket

#     # List for each image
#     images = []
#     for obj in image_bucket.objects.all():  # Create an image URL for each image in bucket
#         images.append(f"https://{image_bucket_name}.s3.amazonaws.com/{obj.key}")

#     # Log each image URL
#     for image in images:
#         print(image)

#     images_html = ""

#     # Add each image to the webpage
#     for image in images:
#         images_html += f"<img src='{image}' alt='S3 Image' style='width:300px;height:auto;'/><br>\n"

#     presigned_api_url = os.environ["PRESIGNED_API_URL"]

#     # add images to html
#     html = html.replace("{imagesBegin}", images_html)
#     html = html.replace("{presignedUrlApi}", presigned_api_url)
#     html = html.replace("{imageBucketName}", image_bucket_name)

#     response = {
#         'statusCode': 200,
#         'headers': {"Content-Type": "text/html",},
#         'body': html
#     }

#     return response