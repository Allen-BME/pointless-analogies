from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)
from constructs import Construct

class PointlessAnalogiesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        test_fun = _lambda.Function(
            self,
            "Index",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambda/")
        )

        endpoint = apigw.LambdaRestApi(
            self,
            "ApiGwEndpoint",
            handler=test_fun,
            rest_api_name="IndexApi"
        )

        # example resource
        # queue = sqs.Queue(
        #     self, "PointlessAnalogiesQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
