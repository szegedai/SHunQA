from pydantic_settings import BaseSettings

from elasticsearch import Elasticsearch
from pymongo import MongoClient


class Environment(BaseSettings):
    mongo_url: str

    elastic_url: str
    elastic_user: str
    elastic_password: str
 
    elastic_index: str
    retriever_size: int
    retriever_contriever_weight: int

    debug: bool = False
    urls: dict = {}


environment = Environment()  # type: ignore

environment.urls = {
    "swagger": "/docs" if environment.debug else None,
    "redoc": "/redoc" if environment.debug else None,
}

elasticsearch_connection = Elasticsearch(
    environment.elastic_url,
    basic_auth=(environment.elastic_user, environment.elastic_password),
    verify_certs=False,
)

mongo_client = MongoClient(environment.mongo_url)