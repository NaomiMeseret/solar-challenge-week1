from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import re

import pandas as pd
import streamlit as st


DATA_DIR = Path("data")
KNOWN_COUNTRIES = ["Benin", "Sierra Leone", "Togo"]
METRICS = ["GHI", "DNI", "DHI"]


def _slug(name: str) -> str:
    """Normalize a country name to a filename-friendly slug.
    Example: "Sierra Leone" -> "sierra_leone"
    """
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower())


def _find_clean_file(country: str, data_dir: Path = DATA_DIR) -> Path | None:
    """Find a cleaned CSV for a given country in data/.
    Tries exact pattern "<slug>_clean.csv" and falls back to any CSV
    containing the slug and the word "clean".
    """
    slug = _slug(country)
    exact = data_dir / f"{slug}_clean.csv"
    if exact.exists():
        return exact

    candidates: List[Path] = []
    for fp in data_dir.glob("*.csv"):
        name = fp.name.lower()
        if slug in name and "clean" in name:
            candidates.append(fp)
    if candidates:
        # deterministic order
        return sorted(candidates)[0]
    return None


@st.cache_data(show_spinner=False)
def load_country(country: str) -> pd.DataFrame:
    """Load a single country's cleaned dataset and attach Country column.
    Returns empty DataFrame if file is not found.
    """
    fp = _find_clean_file(country)
    if fp is None:
        return pd.DataFrame()

    df = pd.read_csv(fp)
    # Standardize timestamp column if present
    ts_col = None
    for col in df.columns:
        if isinstance(col, str) and col.strip().lower() == "timestamp":
            ts_col = col
            break
    if ts_col:
        df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
        if ts_col != "Timestamp":
            df = df.rename(columns={ts_col: "Timestamp"})

    df["Country"] = country
    return df


@st.cache_data(show_spinner=False)
def load_countries(countries: Iterable[str]) -> pd.DataFrame:
    frames = [load_country(c) for c in countries]
    frames = [f for f in frames if not f.empty]
    if not frames:
        return pd.DataFrame()
    df_all = pd.concat(frames, ignore_index=True)
    return df_all


@st.cache_data(show_spinner=False)
def available_countries() -> List[str]:
    present: List[str] = []
    for c in KNOWN_COUNTRIES:
        if _find_clean_file(c) is not None:
            present.append(c)
    return present


def summary_table(df_all: pd.DataFrame, metrics: List[str] = METRICS) -> pd.DataFrame:
    metrics_present = [m for m in metrics if m in df_all.columns]
    if not metrics_present:
        return pd.DataFrame()
    summary = (
        df_all.groupby("Country")[metrics_present]
              .agg(["mean", "median", "std"]).round(2)
              .sort_index()
    )
    return summary


def avg_ghi(df_all: pd.DataFrame) -> pd.Series:
    if "GHI" not in df_all.columns:
        return pd.Series(dtype=float)
    return df_all.groupby("Country")["GHI"].mean().sort_values(ascending=False)
