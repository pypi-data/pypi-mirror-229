import os
import time
from typing import List

try:
    import pinecone

    PINECONE_CLIENT_INSTALLED = True
except ImportError:
    PINECONE_CLIENT_INSTALLED = False

from chainfury import model_registry, Secret
from chainfury.components.const import Env, ComponentMissingError


# https://docs.trychroma.com/usage-guide#using-where-filters
# $eq - equal to (string, int, float)
# $ne - not equal to (string, int, float)
# $gt - greater than (int, float)
# $gte - greater than or equal to (int, float)
# $lt - less than (int, float)
# $lte - less than or equal to (int, float)
# {"$contains": "search_string"}
# $and
# $or


def write_pinecone(
    items: List[str],
    index_name: str,
    pinecone_api_key: Secret = Secret(""),
    piencone_env: Secret = Secret(""),
    embedding_model: str = "openai-embedding",
    model_data: dict = {},
    metric: str = "cosine",
    create_if_not_present: bool = False,
):
    pinecone.init(
        api_key=Env.PINECONE_API_KEY(pinecone_api_key.value),
        environment=Env.PINECONE_ENV(piencone_env.value),
    )

    # create an embeddings first for one item so in case the index does not exist we can create it by passing the
    # embedding dimension
    model = model_registry.get(embedding_model)
    out = model(model_data)

    # only create index if it doesn't exist
    if index_name not in pinecone.list_indexes():
        if create_if_not_present:
            pinecone.create_index(
                name=index_name,
                dimension=len(dataset.documents.iloc[0]["values"]),
                metric=metric,
                shards=1,
                index_file_size=1024,
            )
            time.sleep(1)  # wait a moment for the index to be fully initialized
        else:
            raise Exception(
                f"Index {index_name} does not exist. Please create it first or set create_if_not_present=True",
            )


def read_pinecone(
    query: str,
    index_name: str,
    pinecone_api_key: Secret = Secret(""),
    piencone_env: Secret = Secret(""),
    embedding_model: str = "openai-embedding",
    metric: str = "cosine",
    create_if_not_present: bool = False,
    model_data: dict = {},
):
    pinecone.init(
        api_key=Env.PINECONE_API_KEY(pinecone_api_key.value),
        environment=Env.PINECONE_ENV(piencone_env.value),
    )

    # create an embeddings first for one item so in case the index does not exist we can create it by passing the
    # embedding dimension
    model = model_registry.get(embedding_model)
    out = model(model_data)

    # only create index if it doesn't exist
    if index_name not in pinecone.list_indexes():
        if create_if_not_present:
            pinecone.create_index(
                name=index_name,
                dimension=len(dataset.documents.iloc[0]["values"]),
                metric=metric,
                shards=1,
                index_file_size=1024,
            )
            time.sleep(1)  # wait a moment for the index to be fully initialized
        else:
            raise Exception(
                f"Index {index_name} does not exist. Please create it first or set create_if_not_present=True",
            )
