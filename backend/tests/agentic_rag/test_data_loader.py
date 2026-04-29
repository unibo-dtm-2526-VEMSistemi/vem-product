import io
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


# We patch pandas.read_csv so no real files needed
LOB_CSV = """LOB Code,Name
01001,CABLAGGI COMMSCOPE
01002,CABLAGGIO ALTERNATIVO
02002,APPARATI CISCO LAN
04001,TELEFONIA IP
99001,ALTRO
"""

ARTICLES_CSV = """codice_articolo,descrizione_articolo,lob_associata_cleaned,inventario,code_prefix,duration_months,brand_vendor,product_family,capacity_unit,desc_token_count,desc_char_len,lob_nome,description_norm,rag_text
ART-001,CISCO SWITCH 24P,2002,Inventario,ART,,CISCO,SWITCH,,50,20,APPARATI CISCO LAN,cisco switch 24p,CISCO SWITCH 24P brand:CISCO family:SWITCH
ART-002,MICROSOFT OFFICE LICENSE,99001,Non in inventario,ART,12.0,MICROSOFT,OFFICE,LICENSE,60,25,ALTRO,microsoft office license,MICROSOFT OFFICE LICENSE brand:MICROSOFT family:OFFICE duration:12.0
ART-003,HP CABLE CAT6,1001,Inventario,ART,,HP,CABLE,,30,15,CABLAGGI COMMSCOPE,hp cable cat6,HP CABLE CAT6 brand:HP family:CABLE
ART-004,CISCO IP PHONE 7920,4001,Inventario,ART,,CISCO,PHONE,,40,18,TELEFONIA IP,cisco ip phone 7920,CISCO IP PHONE 7920 brand:CISCO family:PHONE
ART-005,CABLING ALT KIT,1002,Non in inventario,ART,,GENERIC,CABLE,,35,16,CABLAGGIO ALTERNATIVO,cabling alt kit,CABLING ALT KIT brand:GENERIC family:CABLE
"""

def _make_mock_read_csv(lob_csv=LOB_CSV, articles_csv=ARTICLES_CSV):
    lob_df = pd.read_csv(io.StringIO(lob_csv))
    articles_df = pd.read_csv(io.StringIO(articles_csv))
    call_count = [0]

    def mock_read_csv(path, *args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return lob_df.copy()
        return articles_df.copy()

    return mock_read_csv


def test_load_datasets_returns_two_dataframes():
    from src import data_loader
    # Reset cache so patch takes effect
    data_loader.load_datasets.cache_clear()

    with patch("src.data_loader.pd.read_csv", side_effect=_make_mock_read_csv()):
        lob_df, articles_df = data_loader.load_datasets()

    assert len(lob_df) == 5
    assert "LOB Code" in lob_df.columns
    assert "Name" in lob_df.columns


def test_load_datasets_zero_pads_lob_codes():
    from src import data_loader
    data_loader.load_datasets.cache_clear()

    with patch("src.data_loader.pd.read_csv", side_effect=_make_mock_read_csv()):
        _, articles_df = data_loader.load_datasets()

    assert "lob_code_str" in articles_df.columns
    # Integer 2002 → "02002" (5 chars matching max len in lob_codes.csv)
    assert articles_df.loc[articles_df["codice_articolo"] == "ART-001", "lob_code_str"].iloc[0] == "02002"


def test_load_datasets_drops_empty_rag_text():
    """Rows where rag_text is NaN/empty must be dropped."""
    articles_with_nan = ARTICLES_CSV + "ART-006,EMPTY TEXT,2002,Inventario,ART,,CISCO,SWITCH,,50,20,APPARATI CISCO LAN,empty,\n"
    from src import data_loader
    data_loader.load_datasets.cache_clear()

    with patch("src.data_loader.pd.read_csv", side_effect=_make_mock_read_csv(articles_csv=articles_with_nan)):
        _, articles_df = data_loader.load_datasets()

    # ART-006 has empty rag_text and should be dropped
    assert "ART-006" not in articles_df["codice_articolo"].values


def test_get_train_test_split_proportions():
    from src import data_loader
    data_loader.load_datasets.cache_clear()

    with patch("src.data_loader.pd.read_csv", side_effect=_make_mock_read_csv()):
        train_df, test_df = data_loader.get_train_test_split()

    total = len(train_df) + len(test_df)
    assert total == 5  # 5 mock articles


def test_get_article_info_found():
    from src import data_loader
    data_loader.load_datasets.cache_clear()

    with patch("src.data_loader.pd.read_csv", side_effect=_make_mock_read_csv()):
        train_df, _ = data_loader.get_train_test_split()

    # Use the train set — ART-001 should be in train (all go to train with 5 rows)
    # Find any article that's in the train set
    any_code = train_df.iloc[0]["codice_articolo"]
    result = data_loader.get_article_info(any_code, train_df)

    assert result is not None
    assert result["codice_articolo"] == any_code
    assert "descrizione_articolo" in result
    assert "lob_code_str" in result


def test_get_article_info_not_found():
    from src import data_loader
    data_loader.load_datasets.cache_clear()

    with patch("src.data_loader.pd.read_csv", side_effect=_make_mock_read_csv()):
        train_df, _ = data_loader.get_train_test_split()

    result = data_loader.get_article_info("NONEXISTENT-999", train_df)
    assert result is None


def test_get_lob_codes_returns_dataframe():
    from src import data_loader
    data_loader.load_datasets.cache_clear()

    with patch("src.data_loader.pd.read_csv", side_effect=_make_mock_read_csv()):
        lob_df = data_loader.get_lob_codes()

    assert len(lob_df) > 0
    assert "LOB Code" in lob_df.columns
