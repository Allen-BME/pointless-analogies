import boto3
import uuid
import os
import json
from urllib.parse import unquote
from urllib.parse import unquote_plus
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def delete_table_item(table, key: str):
    table_response = table.delete_item(
            Item = {
                "ImageHash": key,
            }
        )
    print(table_response)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('lambda')
    TABLE_NAME = os.environ['TABLE_NAME']
    CATEGORIES_FUNCTION_NAME = os.environ['CATEGORIES_FUNCTION_NAME']
    table = dynamodb.Table(TABLE_NAME)

    # Print event for debugging
    print(json.dumps(event, indent = 2))

    # Pre-define variables to be accessable to return function
    response = 0
    table_response = 0

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        print(f"The bucket name is {bucket}")
        key: str = record['s3']['object']['key']
        print(f"The name of the object put into the bucket is {key}")

        # Quick fix to prevent the lambda from trying to rename an already
        # renamed file
        if key.startswith("uniq-"):
            print("Duplicate found. Continuing")
            continue

        new_key = f"uniq-{uuid.uuid4()}"

        print(f"Created image hash {new_key} to replace {key}")

        response = client.invoke(
            FunctionName = CATEGORIES_FUNCTION_NAME,
            InvocationType = 'RequestResponse'
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

        # If the original object filename has a space or other character that can't be used in a url,
        # the filename is sent in the event with some characters replaced. This try/catch mechanism
        # deals with that problem
        try:
            print(f"copying object with key={key} into bucket={bucket} and giving it a new key={new_key}")
            s3.copy_object(Bucket=bucket, Key=new_key, CopySource=f"{bucket}/{key}")
            print(f"deleting object with key={key} from bucket={bucket}")
            s3.delete_object(Bucket=bucket, Key=key)  
        except ClientError as e:
            # There was an invalid character in the original filename. Try using unquote to fix the error
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"The key {key} does not match any keys in the image bucket. Replacing url characters and trying again")
                try:
                    key = unquote(key)
                    print(f"copying object with key={key} into bucket={bucket} and giving it a new key={new_key}")
                    s3.copy_object(Bucket=bucket, Key=new_key, CopySource=f"{bucket}/{key}")
                    print(f"deleting object with key={key} from bucket={bucket}")
                    s3.delete_object(Bucket=bucket, Key=key)  
                except ClientError as e:
                    # After using unquote there was still an invalid character. Try using unquote_plus to fix the error
                    if e.response['Error']['Code'] == 'NoSuchKey':
                        print(f"The key {key} does not match any keys in the image bucket. Replacing + characters and trying again")
                        try:
                            key = unquote_plus(key)
                            print(f"copying object with key={key} into bucket={bucket} and giving it a new key={new_key}")
                            s3.copy_object(Bucket=bucket, Key=new_key, CopySource=f"{bucket}/{key}")
                            print(f"deleting object with key={key} from bucket={bucket}")
                            s3.delete_object(Bucket=bucket, Key=key)  
                        except ClientError as e:
                            print(f"An unexpected error occurred: {e}")
                            delete_table_item(new_key)
                    else:
                        print(f"An unexpected error occurred: {e}")
                        delete_table_item(new_key)
            else:
                print(f"An unexpected error occurred: {e}")
                delete_table_item(new_key)
        except Exception as e:
            # There was an unexpected error
            print(f"An unexpected error occurred: {e}")         
    
    return {
        "statusCode": 200,
        "body": f"Item added to bucket and table. {response}\n\n\n{table_response}"
    }