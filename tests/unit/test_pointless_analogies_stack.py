import aws_cdk as core
import aws_cdk.assertions as assertions

from pointless_analogies.pointless_analogies_stack import PointlessAnalogiesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in pointless_analogies/pointless_analogies_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PointlessAnalogiesStack(app, "pointless-analogies")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
