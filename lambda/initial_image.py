import boto3
import os

def initial_image(event, context):
    dynamodb = boto3.resource('dynamodb')
    TABLE_NAME = os.environ['TABLE_NAME']
    table = dynamodb.Table(TABLE_NAME)

    # Put item in table
    response = table.put_item(
        Item = {
            "ImageHash": "Test Hash",
            "Category1": "Test Category 1",
            "Category2": "Test Category 2",
            "Category1Votes": 0,
            "Category2Votes": 0
        }
    )

    return {
        "statusCode": 200,
        "body": f"Initial item added to table. Response: {response}"
    }






