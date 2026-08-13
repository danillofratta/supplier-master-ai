from __future__ import annotations


def build_policy_index_mapping(*, dimensions: int) -> dict:
    if dimensions <= 0:
        raise ValueError("Embedding dimensions must be greater than zero.")

    return {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                "document_id": {"type": "keyword"},
                "chunk_id": {"type": "keyword"},
                "title": {"type": "text"},
                "content": {"type": "text"},
                "policy_type": {"type": "keyword"},
                "version": {"type": "keyword"},
                "effective_date": {"type": "date"},
                "position": {"type": "integer"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dimensions,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil"
                    },
                },
            }
        },
    }
