import json

def lambda_handler(event, context):
    """
    Lambda function to handle votes.
    Receives the vote from query string parameters via API Gateway and returns an appropriate response.
    """
    # Log the event for debugging
    print("Received event:", json.dumps(event, indent=2))

    # Extract the 'vote' parameter from query string parameters
    query_params = event.get("queryStringParameters", {})
    vote = query_params.get("vote", None)

    # Determine the response based on the vote value
    if vote == "Category1Vote":
        response_message = "Voted for Category 1"
    elif vote == "Category2Vote":
        response_message = "Voted for Category 2"
    else:
        response_message = "Invalid vote or no vote received"

    # Return a structured response
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({"message": response_message})
    }

# import json
# from urllib.parse import parse_qs

# def lambda_handler(event, context):
#     """
#     Lambda function to handle votes.
#     Receives the vote from query string parameters via API Gateway and returns an appropriate response.
#     """
#     # Log the event for debugging
#     print("Received event:", json.dumps(event, indent=2))

#     # Extract query string parameters
#     query_params = event.get("queryStringParameters", {})
    
#     # Determine the vote and craft a response
#     if "vote" in query_params:
#         vote = query_params["vote"]
#         if vote == "Category1Vote":
#             message = "Voted for Category 1"
#         elif vote == "Category2Vote":
#             message = "Voted for Category 2"
#         else:
#             message = "Invalid vote option"
#     else:
#         message = "No vote parameter provided"
    
#     # Return the response
#     return {
#         "statusCode": 200,
#         "headers": {
#             "Content-Type": "text/html"
#         },
#         "body": f"""
#         <!DOCTYPE html>
#         <html>
#         <head><title>Vote Response</title></head>
#         <body>
#             <h1>{message}</h1>
#         </body>
#         </html>
#         """
#     }

# import json
# import os
# import boto3

# # Initialize the DynamoDB client
# dynamodb = boto3.resource("dynamodb")
# TABLE_NAME = os.environ['TABLE_NAME']
# table = dynamodb.Table(TABLE_NAME)

# def lambda_handler(event, context):
#     # Parse the request body
#     body = json.loads(event.get("body", "{}"))
#     image_hash = body.get("ImageHash")
#     attribute_name = body.get("AttributeName")
#     new_value = body.get("NewValue")

#     if not image_hash or not attribute_name or new_value is None:
#         return {
#             "statusCode": 400,
#             "body": json.dumps({"error": "Missing required fields"})
#         }

#     # Update the DynamoDB table
#     response = table.update_item(
#         Key={"ImageHash": image_hash},
#         UpdateExpression=f"SET #attr = :val",
#         ExpressionAttributeNames={"#attr": attribute_name},
#         ExpressionAttributeValues={":val": new_value},
#         ReturnValues="UPDATED_NEW"
#     )

#     return {
#         "statusCode": 200,
#         "body": json.dumps({
#             "message": "Item updated successfully",
#             "updatedAttributes": response.get("Attributes"),
#         })
#     }
