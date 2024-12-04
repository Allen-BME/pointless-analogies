import boto3
import uuid
import os
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('lambda')
    TABLE_NAME = os.environ['TABLE_NAME']
    table = dynamodb.Table(TABLE_NAME)

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key: str = record['s3']['object']['key']

        # Quick fix to prevent the lambda from trying to rename an already
        # renamed file
        if key.startswith("uniq-"):
            print("Duplicate found. Continuing")
            continue

        new_key = f"uniq-{uuid.uuid4()}"

        print(f"Created image hash {new_key} to replace {key}")

        response = client.invoke(
            FunctionName='get-categories',
            InvocationType='RequestResponse'
        )

        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        categories: str = response_payload['body'] if 'body' in response_payload else response_payload

        split_categories = categories.split('-')

        category1 = split_categories[0]
        category2 = split_categories[1]

        print(f"Got the two categories {category1} and {category2}")

        table_response = table.put_item(
            Item = {
                "ImageHash": new_key,
                "Category1": category1,
                "Category2": category2,
                "Category1Votes": 0,
                "Category2Votes": 0
            }
        )

        s3.copy_object(Bucket=bucket, Key=new_key, CopySource=f"{bucket}/{key}")
        s3.delete_object(Bucket=bucket, Key=key)
    
    return {
        "statusCode": 200,
        "body": f"Item added to bucket and table. {response}\n\n\n{table_response}"
    }