from aws_cdk import App

from cdk.stack import GraphDatastoreStack


app = App()

GraphDatastoreStack(
    app,
    "GraphDatastore",
    env={
        "account": "0123456789",
        "region": "us-east-1",
    },
)

app.synth()
