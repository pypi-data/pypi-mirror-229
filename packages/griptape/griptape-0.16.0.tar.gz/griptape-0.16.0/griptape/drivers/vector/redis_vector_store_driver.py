import redis
import json
import logging
import numpy as np
from griptape import utils
from typing import Optional, List
from attr import define, field, Factory
from griptape.drivers import BaseVectorStoreDriver
from redis.commands.search.query import Query
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
logging.basicConfig(level=logging.WARNING)


@define
class RedisVectorStoreDriver(BaseVectorStoreDriver):
    host: str = field(kw_only=True)
    port: int = field(kw_only=True)
    db: int = field(kw_only=True, default=0)
    password: Optional[str] = field(default=None, kw_only=True)
    index: str = field(kw_only=True)

    client: redis.Redis = field(
        default=Factory(lambda self: redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=False
        ), takes_self=True)
    )

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))
        key = self._generate_key(vector_id, namespace)
        bytes_vector = json.dumps(vector).encode("utf-8")

        mapping = {
            "vector": np.array(vector, dtype=np.float32).tobytes(),
            "vec_string": bytes_vector
        }

        if meta:
            mapping["metadata"] = json.dumps(meta)

        self.client.hset(key, mapping=mapping)

        return vector_id

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        key = self._generate_key(vector_id, namespace)
        result = self.client.hgetall(key)
        vector = np.frombuffer(result[b"vector"], dtype=np.float32).tolist()
        meta = json.loads(result[b"metadata"]) if b"metadata" in result else None

        return BaseVectorStoreDriver.Entry(
            id=vector_id,
            meta=meta,
            vector=vector,
            namespace=namespace
        )

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        pattern = f'{namespace}:*' if namespace else '*'
        keys = self.client.keys(pattern)

        return [
            self.load_entry(key.decode("utf-8"), namespace=namespace)
            for key in keys
        ]

    def query(
            self, query: str, count: Optional[int] = None, namespace: Optional[str] = None, **kwargs
    ) -> List[BaseVectorStoreDriver.QueryResult]:
        vector = self.embedding_driver.embed_string(query)

        query_expression = (
            Query(f"*=>[KNN {count or 10} @vector $vector as score]")
            .sort_by("score")
            .return_fields("id", "score", "metadata", "vec_string")
            .paging(0, count or 10)
            .dialect(2)
        )

        query_params = {
            "vector": np.array(vector, dtype=np.float32).tobytes()
        }

        results = self.client.ft(self.index).search(query_expression, query_params).docs

        query_results = []
        for document in results:
            metadata = getattr(document, "metadata", None)
            namespace = document.id.split(":")[0] if ":" in document.id else None
            vector_float_list = json.loads(document["vec_string"])
            query_results.append(
                BaseVectorStoreDriver.QueryResult(
                    vector=vector_float_list,
                    score=float(document['score']),
                    meta=metadata,
                    namespace=namespace
                )
            )
        return query_results

    def create_index(self, namespace: Optional[str] = None, vector_dimension: Optional[int] = None) -> None:
        try:
            self.client.ft(self.index).info()
            logging.warning("Index already exists!")
        except:
            schema = (
                TagField("tag"),
                VectorField("vector",
                            "FLAT", {
                                "TYPE": "FLOAT32",
                                "DIM": vector_dimension,
                                "DISTANCE_METRIC": "COSINE",
                    }
                ),
            )

            doc_prefix = self._get_doc_prefix(namespace)
            definition = IndexDefinition(prefix=[doc_prefix], index_type=IndexType.HASH)
            self.client.ft(self.index).create_index(fields=schema, definition=definition)

    def _generate_key(self, vector_id: str, namespace: Optional[str] = None) -> str:
        return f'{namespace}:{vector_id}' if namespace else vector_id

    def _get_doc_prefix(self, namespace: Optional[str] = None) -> str:
        """Get the document prefix based on the provided namespace."""
        return f'{namespace}:' if namespace else ""
