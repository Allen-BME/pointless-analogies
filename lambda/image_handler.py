import boto3
import uuid

s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        new_key = f"uniq-{uuid.uuid4()}"
        s3.copy_object(Bucket=bucket, Key=new_key, CopySource=f"{bucket}/{key}")
        s3.delete_object(Bucket=bucket, Key=key)
    
    return "Image successfully renamed"