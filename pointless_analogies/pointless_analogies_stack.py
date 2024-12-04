from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    RemovalPolicy,
    Duration,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    custom_resources as cr,
    aws_s3_notifications as s3n,
)
from constructs import Construct
import json
import os
import shutil

def replace_placeholder(file_path, placeholder, replacement):
    with open(file_path, "r") as file:
        content = file.read()
    content = content.replace(placeholder, replacement)
    with open(file_path, "w") as file:
        file.write(content)

class PointlessAnalogiesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # # Add S3 Bucket to stack
        # image_bucket = s3.Bucket(
        #     self,
        #     "PA_Images",  # Picture bucket ID
        #     versioned=False,  # Do not allow multiple versions of the same file
        #     # Turn off blocks for public access. May want to change for final implementation
        #     block_public_access=s3.BlockPublicAccess(
        #         block_public_acls=False,
        #         block_public_policy=False,
        #         ignore_public_acls=False,
        #         restrict_public_buckets=False
        #     ),
        #     public_read_access=True,  # Pictures are publicly accessible
        #     removal_policy=RemovalPolicy.DESTROY,  # Delete all pictures when stack is deleted
        #     auto_delete_objects=True,  # Auto-delete images when stack is deleted
        #     bucket_name="pointless-analogies-images"  # Picture bucket name
        # )

        # web_bucket = s3.Bucket(
        #     self,
        #     "PA_Web_Content",  # Web content bucket ID
        #     versioned=False,  # Do not allow multiple versions of the same file
        #     #Turn off blocks for public access. May want to change for final implementation
        #     block_public_access=s3.BlockPublicAccess(
        #         block_public_acls=False,
        #         block_public_policy=False,
        #         ignore_public_acls=False,
        #         restrict_public_buckets=False
        #     ),
        #     public_read_access=True,  # Web content is publicly accessible
        #     removal_policy=RemovalPolicy.DESTROY,  # Delete all web content when stack is deleted
        #     auto_delete_objects=True,  # Auto-delete images when stack is destroyed
        #     bucket_name="pointless-analogies-web-content"  # Web content bucket name
        # )
        
        # Create a DynamoDB table to store voting data
        table = dynamodb.TableV2(
            scope = self,
            id = "PointlessAnalogiesVotesTable",
            table_name = "PointlessAnalogiesVotesTable",
            partition_key = dynamodb.Attribute(name = "ImageHash", type = dynamodb.AttributeType.STRING),
            removal_policy = RemovalPolicy.DESTROY,
        )

        # Create a lambda function to add an initial image to the database
        initial_image = _lambda.Function(
            scope = self,
            id = "PointlessAnalogiesInitialImage",
            function_name = "PointlessAnalogiesInitialImage",
            runtime = _lambda.Runtime.PYTHON_3_11,
            # Name of the function to be called by the lambda
            handler = "initial_image.initial_image",
            # Specify the file to take the code from
            code = _lambda.Code.from_asset("lambda/"),
            # Increase lambda function timeout to 30 seconds to make sure the database has time to be initialized
            timeout = Duration.seconds(30)
        )

        # Add the name of the table to the initial_image lambda function
        initial_image.add_environment("TABLE_NAME", table.table_name)

        # Allow initial_image to read and write from the table
        table.grant_write_data(initial_image)
        table.grant_read_data(initial_image)

        vote_function = _lambda.Function(
            scope = self,
            id = "PointlessAnalogiesVoteFunction",
            function_name = "PointlessAnalogiesVoteFunction",
            runtime = _lambda.Runtime.PYTHON_3_11,
            handler = "vote.lambda_handler",
            code = _lambda.Code.from_asset("lambda/"),
            timeout = Duration.seconds(60),
        )

        # Add the name of the table to the initial_image lambda function
        vote_function.add_environment("TABLE_NAME", table.table_name)

        # Allow initial_image to read and write from the table
        table.grant_write_data(vote_function)
        table.grant_read_data(vote_function)

        api = apigw.LambdaRestApi(
            scope = self,
            id = "VoteApi",
            handler = vote_function, 
            proxy = True
        )

        # Replace the placeholder in the HTML file with the API Gateway URL
        html_dir = "./html"
        updated_html_dir = "./html_temp"
        if os.path.exists(updated_html_dir):
            shutil.rmtree(updated_html_dir)  # Clean up previous temporary directory
        shutil.copytree(html_dir, updated_html_dir)  # Create a temporary directory

        html_file_path = os.path.join(updated_html_dir, "index.html")
        replace_placeholder(html_file_path, "{{API_GATEWAY_URL}}", api.url)

        bucket = s3.Bucket(
            scope = self,
            id = "WebAppBucket",
            website_index_document = "index.html",
            #public_read_acess = True
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )
        bucket.grant_public_access()

        # Deploy the HTML file to the S3 bucket
        s3_deployment.BucketDeployment(
            scope = self, 
            id = "DeployWebApp",
            destination_bucket = bucket,
            sources = [s3_deployment.Source.asset(updated_html_dir)]
        )

        # Create custom resource provider to manage the custom resource that adds an initial image to the table
        initial_image_provider = cr.Provider(
            scope = self,
            id = "PointlessAnalogiesInitialImageProvider",
            on_event_handler = initial_image
        )

        # Create custom resource to call the lambda function that adds an initial image to the table
        initial_image_resource = cr.AwsCustomResource(
            scope = self,
            id = "PointlessAnalogiesInitialImageResource",
            function_name = "PointlessAnalogiesInitialImageResourceFunction",
            # Define the function to call when the stack is created
            on_create = cr.AwsSdkCall(
                service = "Lambda",
                action = "invoke",
                parameters = {
                    "FunctionName": initial_image.function_name,
                    "InvocationType": "RequestResponse",
                    "Payload": "{}"
                },
                physical_resource_id = cr.PhysicalResourceId.of("PointlessAnalogiesInitialImageResourceID")
            ),
            policy = cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions = ["lambda:InvokeFunction"],
                    resources = [initial_image.function_arn]
                )
            ])
        )

        # Output the bucket website URL and API endpoint
        self.bucket_url = bucket.bucket_website_url
        self.api_url = api.url

        # # Add Lambda function that serves as site index
        # test_fun = _lambda.Function(
        #     self,
        #     "Index",  # Lambda ID
        #     runtime=_lambda.Runtime.PYTHON_3_11,  # Python version
        #     handler="index.lambda_handler",  # Name of the method within index.py
        #     code=_lambda.Code.from_asset("lambda/"),  # Specify source location
        #     # Increase lambda function timeout to 30 seconds.
        #     # This is needed since getting the objects from S3 takes more time than
        #     # the default 25 ms
        #     timeout=Duration.seconds(30),
        #     # Add the bucket name to the environment.
        #     # This is needed as the bucket name that cdk generates is random
        #     environment={
        #         "BUCKET_NAME": image_bucket.bucket_name 
        #     }
        # )

        # # Add an API Gateway REST API that serves to call the lambda function.
        # # This gives us the URL for the website
        # endpoint = apigw.LambdaRestApi(
        #     self,
        #     "IndexApiEndpoint",  # ID to associate api within CDK
        #     handler=test_fun,  # Set handler to be the defined lambda index function
        #     rest_api_name="IndexApi"  # Name of the API
        # )

        # # Grant read access for the image bucket to the index lambda
        # image_bucket.grant_read(test_fun)

        # # Create a policy that gives the ability to list bucket contents of the
        # # image bucket
        # list_bucket_policy = iam.PolicyStatement(
        #     actions=["s3:ListBucket"],  # Allowed actions...
        #     resources=[image_bucket.bucket_arn]  # for this bucket
        # )

        # # Add the defined policy to the lambda function
        # test_fun.role.attach_inline_policy(
        #     iam.Policy(
        #         self,
        #         "ListBucketPolicy",  # Policy ID
        #         statements=[list_bucket_policy]  # Add permissions
        #     )
        # )

        









        # example resource
        # queue = sqs.Queue(
        #     self, "PointlessAnalogiesQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
