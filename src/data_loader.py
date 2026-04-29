from __future__ import annotations

import functools

import pandas as pd
from sklearn.model_selection import train_test_split as sk_split

from config import (
    LOB_CODES_PATH,
    ARTICLES_PATH,
    TEST_SPLIT_RATIO,
    RANDOM_SEED,
)


@functools.lru_cache(maxsize=1)
def load_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and preprocess both CSVs. Cached after first call."""
    lob_df = pd.read_csv(LOB_CODES_PATH)

    articles_df = pd.read_csv(ARTICLES_PATH)

    # Determine zero-pad width from the actual LOB codes in lob_codes.csv
    max_lob_len = lob_df["LOB Code"].astype(str).str.len().max()

    # Pad lob_associata_cleaned to match LOB codes format
    articles_df["lob_code_str"] = (
        articles_df["lob_associata_cleaned"]
        .astype(int)
        .astype(str)
        .str.zfill(max_lob_len)
    )

    # Enrich articles with LOB name from lob_df
    lob_names = lob_df[["LOB Code", "Name"]].copy()
    lob_names["lob_code_str"] = lob_names["LOB Code"].astype(str).str.zfill(max_lob_len)
    lob_names = lob_names[["lob_code_str", "Name"]].rename(columns={"Name": "lob_nome"})
    articles_df = articles_df.merge(lob_names, on="lob_code_str", how="left")

    # Drop rows with missing or empty rag_text
    articles_df = articles_df.dropna(subset=["rag_text"])
    articles_df = articles_df[articles_df["rag_text"].str.strip() != ""]
    articles_df = articles_df.reset_index(drop=True)

    return lob_df, articles_df


def get_train_test_split() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Stratified train/test split on lob_code_str.

    Classes with < 2 samples are moved entirely to train to avoid
    stratification failure.
    """
    _, articles_df = load_datasets()

    counts = articles_df["lob_code_str"].value_counts()
    rare_mask = articles_df["lob_code_str"].isin(counts[counts < 2].index)

    rare_df = articles_df[rare_mask]
    rest_df = articles_df[~rare_mask]

    if len(rest_df) == 0:
        return articles_df.copy(), pd.DataFrame(columns=articles_df.columns)

    train_rest, test_rest = sk_split(
        rest_df,
        test_size=TEST_SPLIT_RATIO,
        random_state=RANDOM_SEED,
        stratify=rest_df["lob_code_str"],
    )

    train_df = pd.concat([train_rest, rare_df], ignore_index=True)
    test_df = test_rest.reset_index(drop=True)

    return train_df, test_df


def get_article_info(article_code: str, df: pd.DataFrame) -> dict | None:
    """Exact match lookup by codice_articolo. Returns dict or None."""
    matches = df[df["codice_articolo"] == article_code]
    if matches.empty:
        return None

    row = matches.iloc[0]
    return {
        "codice_articolo": row["codice_articolo"],
        "descrizione_articolo": str(row.get("descrizione_articolo", "")),
        "lob_code_str": str(row.get("lob_code_str", "")),
        "lob_nome": str(row.get("lob_nome", "")),
        "inventario": str(row.get("inventario", "")),
        "brand_vendor": str(row.get("brand_vendor", "")) if pd.notna(row.get("brand_vendor")) else "",
        "product_family": str(row.get("product_family", "")) if pd.notna(row.get("product_family")) else "",
    }


def get_lob_codes() -> pd.DataFrame:
    """Return full LOB taxonomy DataFrame."""
    lob_df, _ = load_datasets()
    return lob_df
