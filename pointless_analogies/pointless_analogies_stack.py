from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    RemovalPolicy,
    Duration,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_rds as rds,
    aws_iam as iam
)
from constructs import Construct

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

        # Create a VPC, required for the RDS database
        vpc = ec2.Vpc(
            self, "Pointless-Analogies-Vpc",
            max_azs=2
        )

        # Create an RDS database to store voting data
        database = rds.DatabaseInstance(
            self,
            "PointlessAnalogiesRdsDatabase",
            database_name = "PointlessAnalogiesRdsDatabase",
            # Select MYSQL version 8.0.39 as the database type
            engine = rds.DatabaseInstanceEngine.mysql(
                version = rds.MysqlEngineVersion.VER_8_0_39
            ),
            # Instance type is Burstable3 (which means T3) Micro
            instance_type = ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            multi_az = False,
            # Allocate 10 GB storage to the database, autoscale up to 100 GB if needed
            allocated_storage = 10,
            max_allocated_storage = 100,
            # Put the database in the VPC and restrct the database from public internet access except through a NAT gateway
            vpc = vpc,
            vpc_subnets = {
                "subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS
            },
            # Automatically create a user called admin and generate a password for them. These credentials are required to
            # access the database. If the AWS secrets manager module is used (from aws_cdk.aws_secretsmanager import ISecret),
            # credentials can be granted to a lambda function (secret = database.secret \ secret.grant_read(<LAMBDA FUNCTION ROLE>)
            # \ secret.grant_write(<LAMBDA FUNCTION ROLE>)
            credentials = rds.Credentials.from_generated_secret("admin"),

            publicly_accessible = False,
            # Disable deletion protection
            deletion_protection = False,
            # Delete automated backups when the database is deleted
            delete_automated_backups = True,
            # Don't create a snapshot when the database is deleted
            removal_policy = RemovalPolicy.DESTROY
        )








        # example resource
        # queue = sqs.Queue(
        #     self, "PointlessAnalogiesQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
