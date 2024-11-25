from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_iam as iam
)
from constructs import Construct

class PointlessAnalogiesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "PA_Images",  # Picture bucket name
            versioned=False,  # Do not allow multiple versions of the same file
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            public_read_access=True,  # Pictures are publicly accessible
            removal_policy=RemovalPolicy.DESTROY,  # Delete all pictures when stack is deleted
            auto_delete_objects=True  # Auto-delete images when stack is deleted
        )

        test_fun = _lambda.Function(
            self,
            "Index",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambda/"),
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )

        endpoint = apigw.LambdaRestApi(
            self,
            "ApiGwEndpoint",
            handler=test_fun,
            rest_api_name="IndexApi"
        )

        bucket.grant_read(test_fun)

        list_bucket_policy = iam.PolicyStatement(
            actions=["s3:ListBucket"],
            resources=[bucket.bucket_arn]
        )

        test_fun.role.attach_inline_policy(
            iam.Policy(
                self,
                "ListBucketPolicy",
                statements=[list_bucket_policy]
            )
        )
        # example resource
        # queue = sqs.Queue(
        #     self, "PointlessAnalogiesQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
