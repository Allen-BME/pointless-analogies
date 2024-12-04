import json

def lambda_handler(event, context):
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": "Hello from Lambda!",
        "headers": {
            "content-type": "application.json"
        }
    }
    return response