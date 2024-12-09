import json
import boto3
import os
from decimal import Decimal

def vote_page_handler_function(event, context):
    # Get the HTTP method from the event
    http_method = event['requestContext']['http']['method']
    print(f"HTTP Method: {http_method}")

    if (http_method == "GET"):
        return vote_page_initial_function(event, context)
    elif (http_method == "POST"):
        return vote_page_button_function(event, context)
    else:
        return {
            "statusCode": 400,
            "body": f"Invalid request: {http_method}"
        }
    

def vote_page_initial_function(event, context):
    bucket_name: str = os.environ['HTML_BUCKET_NAME']
    html_name: str = os.environ['HTML_FILE_NAME']
    image_bucket_name: str = os.environ['IMAGE_BUCKET_NAME']
    table_name: str = os.environ['TABLE_NAME']
    api_endpoint: str = os.environ['API_ENDPOINT']

    # Access query string parameters
    query_params = event.get('queryStringParameters', {})
    image_hash: str = ""
    if query_params:
        image_hash = query_params.get('ImageHash', '')
    print(f"The image hash is {image_hash}")

    # Create a new S3 client to access buckets
    client = boto3.client('s3')

    # Get an object representing the table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    dynamodb_response = table.get_item(
        Key = {
            "ImageHash": image_hash
        }
    )
    print(dynamodb_response)
    item = dynamodb_response.get('Item')
    # Get the name of Category 1
    category_1_name = item.get('Category1', 'No Category1 found')
    print(f"Category1Name is {category_1_name}")
    # Get the name of Category 2
    category_2_name = item.get('Category2', 'No Category2 found')
    print(f"Category2Name is {category_2_name}")

    # Get the html stored in the bucket under html_name
    s3_response = client.get_object(
        Bucket = bucket_name,
        Key = html_name
    )
    html: str = s3_response['Body'].read().decode('utf-8') # s3_response['Body'] is a StreamingBody

    # Replace {apiEndpoint} in the html with the actual endpoint
    html = html.replace("{apiEndpoint}", api_endpoint)
    # Replace {image} in the html with the actual image address
    image_url = f"https://{image_bucket_name}.s3.amazonaws.com/{image_hash}"
    html = html.replace("{image}", image_url)
    html = html.replace("{ImageHash}", f'"{image_hash}"')
    # Replace {Category1} with the name of Category 1
    html = html.replace("{Category1}", category_1_name)
    # Replace {Category2} with the name of Category 2
    html = html.replace("{Category2}", category_2_name)

    # Give the html from the bucket to the user
    function_response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": html.encode('utf-8'),
        "headers": {
            "content-type": "text/html"
        }
    }
    return function_response

def vote_page_button_function(event, context):
    bucket_name: str = os.environ['HTML_BUCKET_NAME']
    table_name: str = os.environ['TABLE_NAME']

    # Get an object representing the table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    try:
        # Parse the incoming JSON data from the user
        request_body = json.loads(event['body'])
        # Extract vote choice from the request body
        voteChoice = request_body.get("voteChoice", "No vote provided. If you see this, something's gone wrong.")
        # Log vote choice
        print(f"Received user vote for {voteChoice}")

        # Update vote count
        image_hash = request_body.get("ImageHash", "No image hash provided. If you see this, something's gone wrong.")
        dynamodb_response = table.get_item(Key = {
            "ImageHash": image_hash
        })
        print(dynamodb_response)
        item = dynamodb_response.get('Item')
        # Get the name of Category 1
        category_1_name = item.get('Category1', 'No Category1 found')
        print(f"Category1Name is {category_1_name}")
        # Get the name of Category 2
        category_2_name = item.get('Category2', 'No Category2 found')
        print(f"Category2Name is {category_2_name}")

        if (voteChoice == category_1_name):
            dynamodb_response = table.update_item(
                Key = {
                    "ImageHash": image_hash
                },
                UpdateExpression = "ADD Category1Votes :one",
                ExpressionAttributeValues = {":one": 1}
            )
        elif (voteChoice == category_2_name):
            dynamodb_response = table.update_item(
                Key = {
                    "ImageHash": image_hash
                },
                UpdateExpression = "ADD Category2Votes :one",
                ExpressionAttributeValues = {":one": 1}
            )
        else:
            return {
            "statusCode": 400,
            "body": f"Invalid Vote: {voteChoice}"
            }
        
        print(dynamodb_response)
        dynamodb_response = table.get_item(
            Key = {
            "ImageHash": image_hash
            },
            ConsistentRead = True
        )
        item = dynamodb_response.get('Item')
        # Get the name of Category 1
        category_1_votes = item.get('Category1Votes', 'No Category1Votes found')
        print(f"There are {category_1_votes} for {category_1_name}")
        # Get the name of Category 2
        category_2_votes = item.get('Category2Votes', 'No Category2Votes found')
        print(f"There are {category_1_votes} for {category_2_name}")

        # Create a response to the user
        response_body = {
            "message": "Vote reveived successfully!",
            "voteChoiceMessage": f"You voted for {voteChoice}.",
            "category1Count": int(category_1_votes) if isinstance(category_1_votes, Decimal) else category_1_votes,
            "category2Count": int(category_2_votes) if isinstance(category_2_votes, Decimal) else category_2_votes
        }
        function_response = {
            "isBase64Encoded": False,
            "statusCode": 200,
            # Convert the dictionary (response_body) to a JSON string
            "body": json.dumps(response_body),
            "headers": {
                "content-type": "application/json"
            }
        }
        return function_response
    except json.JSONDecodeError:
        # Return an error code if the body is not valid JSON
        response_body = {
            "message": "No Vote recieved",
            "error": "Invalid JSON"
        }
        function_response = {
            "isBase64Encoded": False,
            "statusCode": 400,
            # Convert the dictionary (response_body) to a JSON string
            "body": json.dumps(response_body),
            "headers": {
                "content-type": "application/json"
            }
        }
        return function_response