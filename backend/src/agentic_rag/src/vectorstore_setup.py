from __future__ import annotations

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from src.config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_LOB,
    CHROMA_COLLECTION_ASSOCIATIONS,
    EMBEDDING_MODEL,
)

# Module-level client cache — reset to None in tests that need isolation
_chroma_client: chromadb.PersistentClient | None = None
_embedding_function: SentenceTransformerEmbeddingFunction | None = None


def _get_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _chroma_client


def _get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
    return _embedding_function


def _embed_lob_collection(
    collection: chromadb.Collection,
    lob_df,
    batch_size: int = 500,
) -> None:
    """Embed LOB codes into the collection in batches."""
    ids = []
    documents = []
    metadatas = []

    for _, row in lob_df.iterrows():
        code = str(row["LOB Code"])
        name = str(row["Name"])
        ids.append(f"lob_{code}")
        documents.append(f"{code} - {name}")
        metadatas.append({"lob_code": code, "name": name})

    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
        print(f"LOB collection: embedded batch {i // batch_size + 1}")


def _embed_associations_collection(
    collection: chromadb.Collection,
    train_df,
    batch_size: int = 500,
) -> None:
    """Embed article associations using the pre-built rag_text column."""
    ids = []
    documents = []
    metadatas = []

    for idx, row in train_df.iterrows():
        ids.append(f"art_{idx}_{row['codice_articolo']}")
        documents.append(str(row["rag_text"]))
        metadatas.append({
            "codice_articolo": str(row["codice_articolo"]),
            "lob_code_str": str(row["lob_code_str"]),
            "lob_nome": str(row.get("lob_nome", "")),
            "inventario": str(row.get("inventario", "")),
            "descrizione_articolo": str(row.get("descrizione_articolo", "")),
        })

    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
        print(
            f"Associations collection: embedded batch {i // batch_size + 1} "
            f"/ {(len(ids) + batch_size - 1) // batch_size}"
        )


def initialize_vectorstore(train_df, lob_df, force_rebuild: bool = False) -> None:
    """Initialize ChromaDB collections. Skips embedding if already populated."""
    client = _get_client()
    ef = _get_embedding_function()

    lob_collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_LOB,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    assoc_collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_ASSOCIATIONS,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    lob_populated = lob_collection.count() > 0
    assoc_populated = assoc_collection.count() > 0

    if force_rebuild:
        if lob_populated:
            lob_collection.delete(ids=lob_collection.get()["ids"])
        if assoc_populated:
            assoc_collection.delete(ids=assoc_collection.get()["ids"])
        lob_populated = False
        assoc_populated = False

    if not lob_populated:
        print(f"Embedding {len(lob_df)} LOB codes...")
        _embed_lob_collection(lob_collection, lob_df)
        print("LOB collection ready.")

    if not assoc_populated:
        print(f"Embedding {len(train_df)} training articles...")
        _embed_associations_collection(assoc_collection, train_df)
        print("Associations collection ready.")

    if lob_populated and assoc_populated:
        print("Vectorstore already populated — skipping embedding.")


def get_collections() -> tuple[chromadb.Collection, chromadb.Collection]:
    """Return (lob_collection, assoc_collection). Call after initialize_vectorstore."""
    client = _get_client()
    ef = _get_embedding_function()
    lob_col = client.get_or_create_collection(
        name=CHROMA_COLLECTION_LOB,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    assoc_col = client.get_or_create_collection(
        name=CHROMA_COLLECTION_ASSOCIATIONS,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return lob_col, assoc_col
