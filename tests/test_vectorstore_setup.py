import io
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, call


LOB_CSV = """LOB Code,Name
01001,CABLAGGI COMMSCOPE
02002,APPARATI CISCO LAN
"""

TRAIN_CSV = """codice_articolo,descrizione_articolo,lob_code_str,inventario,brand_vendor,product_family,lob_nome,rag_text
ART-001,CISCO SWITCH 24P,02002,Inventario,CISCO,SWITCH,APPARATI CISCO LAN,CISCO SWITCH 24P brand:CISCO family:SWITCH
ART-002,HP CABLE CAT6,01001,Inventario,HP,CABLE,CABLAGGI COMMSCOPE,HP CABLE CAT6 brand:HP family:CABLE
"""


def _make_dfs():
    lob_df = pd.read_csv(io.StringIO(LOB_CSV))
    train_df = pd.read_csv(io.StringIO(TRAIN_CSV))
    return train_df, lob_df


def test_initialize_vectorstore_creates_two_collections():
    train_df, lob_df = _make_dfs()

    mock_chroma_client = MagicMock()
    mock_lob_collection = MagicMock()
    mock_assoc_collection = MagicMock()

    # Simulate empty collections (count = 0) to force rebuild
    mock_lob_collection.count.return_value = 0
    mock_assoc_collection.count.return_value = 0

    mock_chroma_client.get_or_create_collection.side_effect = [
        mock_lob_collection,
        mock_assoc_collection,
    ]

    mock_ef = MagicMock()

    with patch("chromadb.PersistentClient", return_value=mock_chroma_client), \
         patch("chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction", return_value=mock_ef):
        # Import after patching
        import src.vectorstore_setup
        src.vectorstore_setup._chroma_client = None
        src.vectorstore_setup._embedding_function = None
        src.vectorstore_setup.initialize_vectorstore(train_df, lob_df)

    assert mock_chroma_client.get_or_create_collection.call_count == 2


def test_initialize_vectorstore_skips_if_populated():
    """If collections already have data, skip rebuilding."""
    train_df, lob_df = _make_dfs()

    mock_chroma_client = MagicMock()
    mock_lob_collection = MagicMock()
    mock_assoc_collection = MagicMock()

    # Simulate populated collections
    mock_lob_collection.count.return_value = 2
    mock_assoc_collection.count.return_value = 2

    mock_chroma_client.get_or_create_collection.side_effect = [
        mock_lob_collection,
        mock_assoc_collection,
    ]

    with patch("chromadb.PersistentClient", return_value=mock_chroma_client), \
         patch("chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction", return_value=MagicMock()):
        from src import vectorstore_setup
        # Reset module-level client cache
        vectorstore_setup._chroma_client = None
        vectorstore_setup._embedding_function = None
        initialize_vectorstore = vectorstore_setup.initialize_vectorstore
        initialize_vectorstore(train_df, lob_df)

    # add() should NOT have been called since collections are populated
    mock_lob_collection.add.assert_not_called()
    mock_assoc_collection.add.assert_not_called()


def test_initialize_vectorstore_force_rebuild():
    """force_rebuild=True should re-add even if collections are populated."""
    train_df, lob_df = _make_dfs()

    mock_chroma_client = MagicMock()
    mock_lob_collection = MagicMock()
    mock_assoc_collection = MagicMock()

    mock_lob_collection.count.return_value = 5
    mock_assoc_collection.count.return_value = 5
    # Mock the get() method for delete() to work
    mock_lob_collection.get.return_value = {"ids": ["lob_01001", "lob_02002"]}
    mock_assoc_collection.get.return_value = {"ids": ["art_0_ART-001", "art_1_ART-002"]}

    mock_chroma_client.get_or_create_collection.side_effect = [
        mock_lob_collection,
        mock_assoc_collection,
    ]

    with patch("chromadb.PersistentClient", return_value=mock_chroma_client), \
         patch("chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction", return_value=MagicMock()):
        from src import vectorstore_setup
        vectorstore_setup._chroma_client = None
        vectorstore_setup._embedding_function = None
        vectorstore_setup.initialize_vectorstore(train_df, lob_df, force_rebuild=True)

    mock_lob_collection.delete.assert_called()
    mock_lob_collection.add.assert_called()


def test_get_collections_returns_both():
    """get_collections() returns a (lob_collection, assoc_collection) tuple."""
    mock_chroma_client = MagicMock()
    mock_lob_col = MagicMock()
    mock_assoc_col = MagicMock()
    mock_chroma_client.get_or_create_collection.side_effect = [mock_lob_col, mock_assoc_col]
    mock_ef = MagicMock()

    with patch("chromadb.PersistentClient", return_value=mock_chroma_client), \
         patch("chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction", return_value=mock_ef):
        from src import vectorstore_setup
        vectorstore_setup._chroma_client = None
        vectorstore_setup._embedding_function = None
        lob_col, assoc_col = vectorstore_setup.get_collections()

    assert lob_col is mock_lob_col
    assert assoc_col is mock_assoc_col
    assert mock_chroma_client.get_or_create_collection.call_count == 2
