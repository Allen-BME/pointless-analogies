from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as apigw_integrations,
    RemovalPolicy,
    Duration,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_logs as logs,
    custom_resources as cr,
    CfnOutput,
)
from constructs import Construct
import json
import os
import shutil

class PointlessAnalogiesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # S3 BUCKET DEFINITIONS


        # Add S3 Bucket to stack
        image_bucket = s3.Bucket(
            scope = self,
            id = "pa-image-bucket",  # Picture bucket ID
            versioned=False,  # Do not allow multiple versions of the same file
            # Turn off blocks for public access. May want to change for final implementation
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            public_read_access=True,  # Pictures are publicly accessible
            removal_policy=RemovalPolicy.DESTROY,  # Delete all pictures when stack is deleted
            auto_delete_objects=True,  # Auto-delete images when stack is deleted
            bucket_name="pa-image-bucket",  # Picture bucket name
            cors=[s3.CorsRule(
                allowed_headers=["*"],
                allowed_methods=[
                    s3.HttpMethods.PUT,
                    s3.HttpMethods.GET,
                    s3.HttpMethods.POST],
                allowed_origins=["*"])
            ]
        )

        # Add a bucket policy to allow s3:PutObject
        image_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[f"{image_bucket.bucket_arn}/*"],
                principals=[iam.AnyPrincipal()]
            )
        )

        # Create a bucket to store template HTML files
        html_bucket = s3.Bucket(
            scope = self,
            id = "pa-html-bucket",
            bucket_name = "pa-html-bucket",
            block_public_access=s3.BlockPublicAccess(
                block_public_acls = True,
                block_public_policy = True,
                ignore_public_acls = True,
                restrict_public_buckets = True
            ),
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )

        # Deploy the all HTML files in html_templates to html_bucket. This is automatically run
        html_bucket_deploy_files = s3_deployment.BucketDeployment(
            scope = self, 
            id = "pa-deploy-html-templates",
            destination_bucket = html_bucket,
            sources = [s3_deployment.Source.asset("./html_templates/")]
        )


        # DYNAMODB TABLE DEFINITION


        # Create a DynamoDB table to store voting data
        table = dynamodb.TableV2(
            scope = self,
            id = "pa-votes-table",
            table_name = "pa-votes-table",
            partition_key = dynamodb.Attribute(name = "ImageHash", type = dynamodb.AttributeType.STRING),
            removal_policy = RemovalPolicy.DESTROY,
        )


        # LAMBDA FUNCTION DEFINITIONS


        # Create a function to display the main page of images and links to vote on them
        main_page_function = _lambda.Function(
            scope = self,
            id = "pa-main-page-function",
            function_name = "pa-main-page-function",
            runtime = _lambda.Runtime.PYTHON_3_11,
            handler = "index.main_page_function",
            code = _lambda.Code.from_asset("lambda/"),
            timeout = Duration.seconds(60)
        )
        image_bucket.grant_read(main_page_function)
        html_bucket.grant_read(main_page_function)
        table.grant_read_data(main_page_function)
        main_page_function.add_environment("IMAGE_BUCKET_NAME", image_bucket.bucket_name)
        main_page_function.add_environment("HTML_BUCKET_NAME", html_bucket.bucket_name)
        main_page_function.add_environment("HTML_FILE_NAME", "main_page.html")
        main_page_function.add_environment("HTML_SNIPPET_NAME", "image_snippet.html")
        main_page_function.add_environment("TABLE_NAME", table.table_name)

        # Create a function to be the handler for the vote path of the HTTP API
        vote_page_handler_function = _lambda.Function(
            scope = self,
            id = "pa-vote-page-handler-function",
            function_name = "pa-vote-page-handler-function",
            runtime = _lambda.Runtime.PYTHON_3_11,
            handler = "vote_page_functions.vote_page_handler_function",
            code = _lambda.Code.from_asset("lambda/"),
            timeout = Duration.seconds(15)
        )
        html_bucket.grant_read(vote_page_handler_function)
        image_bucket.grant_read(vote_page_handler_function)
        table.grant_full_access(vote_page_handler_function)
        vote_page_handler_function.add_environment("HTML_BUCKET_NAME", html_bucket.bucket_name)
        vote_page_handler_function.add_environment("HTML_FILE_NAME", "vote_page.html")
        vote_page_handler_function.add_environment("IMAGE_BUCKET_NAME", image_bucket.bucket_name)
        vote_page_handler_function.add_environment("TABLE_NAME", table.table_name)

        # Function to return two random categories
        get_categories_function = _lambda.Function(
            scope = self,
            id = "pa-get-categories-function",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="categories.get_categories_function",
            code=_lambda.Code.from_asset("lambda/"),
            timeout=Duration.seconds(5),
            function_name="pa-get-categories-function"
        )

        # Create a function to make a unique hash for each image uploaded to the image bucket
        generate_image_hash_function = _lambda.Function(
            scope = self,
            id = "pa-generate-image-hash-function",
            function_name = "pa-generate-image-hash-function",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="image_handler.generate_image_hash_function",
            code=_lambda.Code.from_asset("lambda/"),
            timeout=Duration.seconds(30),
            # role=category_role
        )
        get_categories_function.grant_invoke(generate_image_hash_function)
        image_bucket.grant_read_write(generate_image_hash_function)
        generate_image_hash_function.add_environment("TABLE_NAME", table.table_name)
        generate_image_hash_function.add_environment("CATEGORIES_FUNCTION_NAME", get_categories_function.function_name)
        table.grant_read_write_data(generate_image_hash_function)
        image_bucket_notif = s3n.LambdaDestination(generate_image_hash_function)
        image_bucket.add_event_notification(
            event = s3.EventType.OBJECT_CREATED_PUT,
            dest = image_bucket_notif
        )

        # function to return presigned URL for S3
        generate_presigned_url_function = _lambda.Function(
            self,
            "GeneratePresignedUrlFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="generate_presigned_url.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "BUCKET_NAME": image_bucket.bucket_name,
            }
        )
        image_bucket.grant_put(generate_presigned_url_function)

        # HTTP API DEFINITION AND ROUTES

        # Create an HTTP API to access the lambda functions
        http_api = apigw.HttpApi(
            scope = self,
            id = "pa-http-api",
            api_name = "pa-http-api",
            default_integration = apigw_integrations.HttpLambdaIntegration(
                id = "pa-apigw-main-page-integration",
                handler = main_page_function
            ),
            cors_preflight={
                "allow_origins": ["*"],
                "allow_methods": [
                    apigw.CorsHttpMethod.POST,
                    apigw.CorsHttpMethod.GET,
                    apigw.CorsHttpMethod.PUT,
                    ],
                "allow_headers": ["*"]
            }       
        )
        main_page_function.add_environment("API_ENDPOINT", http_api.api_endpoint)

        # Add a new route to http_api for upload image
        http_api.add_routes(
            path="/generate-presigned-url",
            methods=[apigw.HttpMethod.POST],
            integration=apigw_integrations.HttpLambdaIntegration(
                id="pa-apigw-generate-presigned-url-integration",
                handler=generate_presigned_url_function
            ),
        )
        main_page_function.add_environment("API_ENDPOINT", http_api.api_endpoint)

        # Add new routes to http_api for vote page acces and vote button actions
        http_api.add_routes(
            path = "/vote",
            methods = [apigw.HttpMethod.GET, apigw.HttpMethod.POST],
            integration = apigw_integrations.HttpLambdaIntegration(
                id = "pa-apigw-vote-page-integration",
                handler = vote_page_handler_function
            )
        )
        vote_page_handler_function.add_environment("API_ENDPOINT", http_api.api_endpoint)
        

        CfnOutput(self, id="IndexApiEndpoint", value=http_api.api_endpoint)
