from aws_cdk import (
    Stack
)
from constructs import Construct
import os
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigateway

class KnowlioStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_function = _lambda.Function(self, "MyLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.handler",
            code=_lambda.Code.from_asset(os.path.join(os.path.dirname(__file__), "src"))
        )