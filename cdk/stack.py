from typing import Any

import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from constructs import Construct


class GraphDatastoreStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs: Any):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "Vpc", nat_gateways=0)

        datastore = dynamodb.Table(
            self,
            "Datastore",
            partition_key={
                "name": "pk",
                "type": dynamodb.AttributeType.STRING,
            },
            sort_key={
                "name": "sk",
                "type": dynamodb.AttributeType.STRING,
            },
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        bundling = cdk.BundlingOptions(
            image=cdk.DockerImage("public.ecr.aws/sam/build-python3.8"),
            command=[
                "bash",
                "-c",
                "pip install -r requirements.txt -t /asset-output/python"
                " && cp -au . /asset-output || true",
            ],
        )

        deps_layer = lambda_.LayerVersion(
            self,
            "ApiLayer",
            code=lambda_.Code.from_asset("lambdas/layer", bundling=bundling),
        )

        graphql_fn = lambda_.Function(
            self,
            "GraphQLFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambdas/graphql"),
            handler="package.main.handler",
            layers=[deps_layer],
            memory_size=1024,
            timeout=cdk.Duration.minutes(5),
            environment={
                "DATASTORE_NAME": datastore.table_name,
            },
            log_retention=logs.RetentionDays.THREE_MONTHS,
            vpc=vpc,  # type: ignore
        )
        if graphql_fn.role:
            datastore.grant_read_write_data(graphql_fn.role)

        fn_url = lambda_.FunctionUrl(
            self,
            "GraphQLUrl",
            function=graphql_fn,  # type: ignore
            auth_type=lambda_.FunctionUrlAuthType.NONE,
        )

        cdk.CfnOutput(self, "DatastoreName", value=datastore.table_name)
        cdk.CfnOutput(self, "FunctionUrl", value=fn_url.url)
