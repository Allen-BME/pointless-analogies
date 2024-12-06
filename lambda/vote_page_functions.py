import json
import boto3
import os

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
    # Parse the bucket name, html file name, and api endpoint from the environment
    bucket_name: str = os.environ['HTML_BUCKET_NAME']
    html_name: str = os.environ['HTML_FILE_NAME']
    api_endpoint: str = os.environ['API_ENDPOINT']

    # Create a new S3 client to access buckets
    client = boto3.client('s3')

    # Get the html stored in the bucket under html_name
    s3_response = client.get_object(
        Bucket = bucket_name,
        Key = html_name
    )
    html: str = s3_response['Body'].read().decode('utf-8') # s3_response['Body'] is a StreamingBody

    # Replace {apiEndpoint} in the html with the actual endpoint
    html = html.replace("{apiEndpoint}", f'"{api_endpoint}/vote"')

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
    # Parse the bucket name from the environment
    bucket_name: str = os.environ['HTML_BUCKET_NAME']

    try:
        # Parse the incoming JSON data from the user
        request_body = json.loads(event['body'])
        # Extract vote choice from the request body
        voteChoice = request_body.get("voteChoice", "No vote provided. If you see this, something's gone wrong.")
        # Log vote choice
        print(f"Received user vote for {voteChoice}")

        # MODIFY TO PLACE VOTE IN TABLE

        # Create a response to the user
        response_body = {
            "message": "Vote reveived successfully!",
            "voteChoiceMessage": f"You voted for {voteChoice}."
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