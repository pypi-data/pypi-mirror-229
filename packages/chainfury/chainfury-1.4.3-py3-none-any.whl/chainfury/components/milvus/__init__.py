try:
    from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

    MILVUS_CLIENT_INSTALLED = True
except ImportError:
    MILVUS_CLIENT_INSTALLED = False


class MilvusVectorDBComponent:
    def __init__(self, host: str = "127.0.0.1", port: str = "19530"):
        connections.connect(host=host, port=port)
        pass

    def write(self, collection_name: str):
        pass
