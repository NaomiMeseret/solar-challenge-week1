from __future__ import annotations

import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

try:
    from app.utils import (
        available_countries,
        load_countries,
        summary_table,
        avg_ghi,
        METRICS,
    )
except ModuleNotFoundError:
    # When executed via `streamlit run app/main.py`, Streamlit may set the
    # working module path to the app directory only. Ensure project root is on sys.path.
    ROOT = os.path.dirname(os.path.dirname(__file__))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from app.utils import (
        available_countries,
        load_countries,
        summary_table,
        avg_ghi,
        METRICS,
    )


st.set_page_config(page_title="Cross-Country Solar Dashboard", layout="wide")
sns.set(style="whitegrid", context="talk")

st.title("Cross-Country Solar Comparison Dashboard")
st.markdown(
    "Use this dashboard to compare solar resource metrics across countries. "
    "Data is read locally from the `data/` folder (gitignored)."
)

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    present = available_countries()
    if not present:
        st.warning("No cleaned datasets found. Place *<country>_clean.csv* files in data/.")
    countries = st.multiselect(
        "Select countries",
        options=["Benin", "Sierra Leone", "Togo"],
        default=present if present else ["Benin"],
    )
    metric = st.selectbox("Metric", options=METRICS, index=0)

if not countries:
    st.info("Please select at least one country.")
    st.stop()

# Load data
df_all = load_countries(countries)
if df_all.empty:
    st.error("No data loaded. Ensure cleaned CSVs exist in the data/ folder.")
    st.stop()

# Top row: boxplot and ranking bar chart
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader(f"{metric} Distribution by Country")
    if metric not in df_all.columns:
        st.warning(f"Metric '{metric}' is not present in the loaded data.")
    else:
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.boxplot(data=df_all, x="Country", y=metric, palette="Set2", ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel(f"{metric} (units)")
        ax.set_title(f"{metric} by Country")
        ax.tick_params(axis='x', rotation=15)
        st.pyplot(fig, clear_figure=True)

with col2:
    st.subheader("Ranking by Average GHI")
    ghi_rank = avg_ghi(df_all)
    if ghi_rank.empty:
        st.info("GHI not available for ranking.")
    else:
        rank_df = ghi_rank.reset_index()
        rank_df.columns = ["Country", "Average GHI (W/m²)"]
        st.bar_chart(rank_df.set_index("Country"))
        st.dataframe(rank_df.style.format({"Average GHI (W/m²)": "{:.1f}"}), use_container_width=True)

# Summary table
st.subheader("Summary Table (Mean / Median / Std)")
sum_tbl = summary_table(df_all, metrics=METRICS)
if sum_tbl.empty:
    st.info("No metrics available to summarize.")
else:
    st.dataframe(sum_tbl, use_container_width=True)

st.caption("Tip: Add more countries by placing additional *_clean.csv files in the data/ folder.")
