import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_blank.cdk_blank_stack import CdkBlankStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_blank/cdk_blank_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkBlankStack(app, "cdk-blank")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
