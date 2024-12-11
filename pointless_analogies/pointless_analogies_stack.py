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
        
        # Create a function to display the voting page for a given image
        # vote_page_initial_function = _lambda.Function(
        #     scope = self,
        #     id = "PointlessAnalogiesVotePageInitialFunction",
        #     function_name = "PointlessAnalogiesVotePageInitialFunction",
        #     runtime = _lambda.Runtime.PYTHON_3_11,
        #     handler = "vote_page_functions.vote_page_initial_function",
        #     code = _lambda.Code.from_asset("lambda/"),
        #     timeout = Duration.seconds(30)
        # )
        # html_bucket.grant_read(vote_page_initial_function)
        # image_bucket.grant_read(vote_page_initial_function)
        # table.grant_read_data(vote_page_initial_function)
        # vote_page_initial_function.add_environment("HTML_BUCKET_NAME", html_bucket.bucket_name)
        # vote_page_initial_function.add_environment("HTML_FILE_NAME", "vote_page.html")
        # vote_page_initial_function.add_environment("IMAGE_BUCKET_NAME", image_bucket.bucket_name)
        # vote_page_initial_function.add_environment("TABLE_NAME", table.table_name)

        # Create a function to process votes and display the vote count for a given image
        # vote_page_button_function = _lambda.Function(
        #     scope = self,
        #     id = "PointlessAnalogiesVotePageButtonFunction",
        #     function_name = "PointlessAnalogiesVotePageButtonFunction",
        #     runtime = _lambda.Runtime.PYTHON_3_11,
        #     handler = "vote_page_functions.vote_page_button_function",
        #     code = _lambda.Code.from_asset("lambda/"),
        #     timeout = Duration.seconds(15)
        # )
        # table.grant_full_access(vote_page_button_function)
        # vote_page_button_function.add_environment("HTML_BUCKET_NAME", html_bucket.bucket_name)
        # vote_page_button_function.add_environment("TABLE_NAME", table.table_name)

        # Add Lambda function that serves as site index
        # index_function = _lambda.Function(
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
        #         "IMAGE_BUCKET_NAME": image_bucket.bucket_name,
        #         "HTML_BUCKET_NAME": html_bucket.bucket_name,
        #         "HTML_FILE_NAME": "main_page.html", 
        #     }
        # )
        # image_bucket.grant_read(index_function)
        # html_bucket.grant_read(index_function)
        
        # Create a policy that gives the ability to list bucket contents of the
        # image bucket
        # list_bucket_policy = iam.PolicyStatement(
        #     actions=["s3:ListBucket"],  # Allowed actions...
        #     resources=[image_bucket.bucket_arn]  # for this bucket
        # )
        # Add the defined policy to the lambda function
        # index_function.role.attach_inline_policy(
        #     iam.Policy(
        #         self,
        #         "ListBucketPolicy",  # Policy ID
        #         statements=[list_bucket_policy]  # Add permissions
        #     )
        # )

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

        # category_role = iam.Role(
        #     self,
        #     "CategoryRole",
        #     assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        #     managed_policies=[
        #         iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
        #         iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")
        #     ]
        # )
        # category_invoke_policy = iam.Policy(
        #     self,
        #     "CategoryInvokePolicy",
        #     statements=[
        #         iam.PolicyStatement(
        #             actions=["lambda:InvokeFunction", "logs:CreateLogGroup", "logs:createLogStream", "logs:PutLogEvents"],
        #             resources=[f"arn:aws:lambda:{self.region}:{self.account}:function:get-categories",
        #                        f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/*"]
        #         )
        #     ]
        # )
        # category_role.attach_inline_policy(category_invoke_policy)
        # Create a function to make a unique hash for each image uploaded to the image bucket
        uploaded_images = _lambda.Function(
            self,
            "Uploaded_images",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="image_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda/"),
            timeout=Duration.seconds(30),
            # role=category_role
        )
        get_categories_function.grant_invoke(uploaded_images)
        image_bucket.grant_read_write(uploaded_images)
        uploaded_images.add_environment("TABLE_NAME", table.table_name)
        uploaded_images.add_environment("CATEGORIES_FUNCTION_NAME", get_categories_function.function_name)
        table.grant_read_write_data(uploaded_images)
        image_bucket_notif = s3n.LambdaDestination(uploaded_images)
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
            id = "PointlessAnalogiesHTTPApi",
            api_name = "PointlessAnalogiesHTTPApi",
            default_integration = apigw_integrations.HttpLambdaIntegration(
                id = "PointlessAnalogiesAPIGWMainPageIntegration",
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
                id="PointlessAnalogiesAPIGWGeneratePresignedUrlIntegration",
                handler=generate_presigned_url_function
            ),
        )
        main_page_function.add_environment("API_ENDPOINT", http_api.api_endpoint)

        # Add new routes to http_api for vote page acces and vote button actions
        http_api.add_routes(
            path = "/vote",
            methods = [apigw.HttpMethod.GET, apigw.HttpMethod.POST],
            integration = apigw_integrations.HttpLambdaIntegration(
                id = "PointlessAnalogiesAPIGWVotePageIntegration",
                handler = vote_page_handler_function
            )
        )
        vote_page_handler_function.add_environment("API_ENDPOINT", http_api.api_endpoint)
        # vote_page_initial_function.add_environment("API_ENDPOINT", http_api.api_endpoint)
        # vote_page_button_function.add_environment("API_ENDPOINT", http_api.api_endpoint)
        

        CfnOutput(self, id="IndexApiEndpoint", value=http_api.api_endpoint)

        # # Create a lambda function to add an initial image to the database
        # initial_image = _lambda.Function(
        #     scope = self,
        #     id = "PointlessAnalogiesInitialImage",
        #     function_name = "PointlessAnalogiesInitialImage",
        #     runtime = _lambda.Runtime.PYTHON_3_11,
        #     # Name of the function to be called by the lambda
        #     handler = "initial_image.initial_image",
        #     # Specify the file to take the code from
        #     code = _lambda.Code.from_asset("lambda/"),
        #     # Increase lambda function timeout to 30 seconds to make sure the database has time to be initialized
        #     timeout = Duration.seconds(30)
        # )

        # # Add the name of the table to the initial_image lambda function
        # initial_image.add_environment("TABLE_NAME", table.table_name)

        # # Allow initial_image to read and write from the table
        # table.grant_write_data(initial_image)
        # table.grant_read_data(initial_image)

        # # Create custom resource to call the lambda function that adds an initial image to the table
        # initial_image_resource = cr.AwsCustomResource(
        #     scope = self,
        #     id = "PointlessAnalogiesInitialImageResource",
        #     function_name = "PointlessAnalogiesInitialImageResourceFunction",
        #     # Define the function to call when the stack is created
        #     on_create = cr.AwsSdkCall(
        #         service = "Lambda",
        #         action = "invoke",
        #         parameters = {
        #             "FunctionName": initial_image.function_name,
        #             "InvocationType": "RequestResponse",
        #             "Payload": "{}"
        #         },
        #         physical_resource_id = cr.PhysicalResourceId.of("PointlessAnalogiesInitialImageResourceID")
        #     ),
        #     policy = cr.AwsCustomResourcePolicy.from_statements([
        #         iam.PolicyStatement(
        #             actions = ["lambda:InvokeFunction"],
        #             resources = [initial_image.function_arn]
        #         )
        #     ])
        # )