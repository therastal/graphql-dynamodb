import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import ParserCache, ValidationCache

from . import schema

DEPLOYMENT = os.getenv("DEPLOYMENT_KEY", "local")

graphql_schema = Schema(schema.Query, extensions=[ParserCache(), ValidationCache()])
graphql_app = GraphQLRouter(graphql_schema)

app = FastAPI(root_path=f"/{DEPLOYMENT}")
app.include_router(graphql_app, prefix="/graphql")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

handler = Mangum(app)
