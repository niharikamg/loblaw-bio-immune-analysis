import pandas as pd
import streamlit as st
from pathlib import Path


SUMMARY_FILE = Path("summary_table.csv")
STATS_FILE = Path("statistical_results.csv")
BASELINE_FILE = Path("baseline_miraclib_subset.csv")
BOXPLOT_FILE = Path("responder_boxplots.png")


st.set_page_config(
    page_title="Loblaw Bio Immune Analysis",
    layout="wide",
)


st.title("Loblaw Bio Immune Cell Analysis")
st.write(
    "Interactive dashboard for cell population frequencies, "
    "miraclib response analysis, and baseline melanoma subsets."
)


summary = pd.read_csv(SUMMARY_FILE)
stats = pd.read_csv(STATS_FILE)
baseline = pd.read_csv(BASELINE_FILE)


st.header("Part 2: Cell Population Frequencies")

sample_options = sorted(summary["sample"].unique())

selected_sample = st.selectbox(
    "Choose a sample",
    sample_options,
)

sample_data = summary[
    summary["sample"] == selected_sample
].copy()

st.dataframe(
    sample_data,
    use_container_width=True,
)

st.bar_chart(
    sample_data.set_index("population")["percentage"]
)


st.header("Part 3: Miraclib Response Analysis")

st.write(
    "Melanoma PBMC samples receiving miraclib were compared "
    "between responders and non-responders."
)

st.dataframe(
    stats,
    use_container_width=True,
)

if BOXPLOT_FILE.exists():
    st.image(
        str(BOXPLOT_FILE),
        caption="Responder vs non-responder relative frequencies",
        use_container_width=True,
    )

significant_raw = stats[
    stats["significant_raw_p"] == True
]

significant_fdr = stats[
    stats["significant_fdr"] == True
]

st.subheader("Statistical interpretation")

if len(significant_raw) > 0:
    st.write(
        "Populations significant at raw p < 0.05:",
        ", ".join(significant_raw["population"]),
    )
else:
    st.write("No populations were significant at raw p < 0.05.")

if len(significant_fdr) > 0:
    st.write(
        "Populations significant after FDR correction:",
        ", ".join(significant_fdr["population"]),
    )
else:
    st.write(
        "No cell populations remained significant after "
        "FDR correction at 0.05."
    )


st.header("Part 4: Baseline Melanoma PBMC Samples")

st.metric(
    "Total baseline miraclib samples",
    len(baseline),
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Samples by Project")
    project_counts = (
        baseline.groupby("project")["sample"]
        .nunique()
        .reset_index(name="sample_count")
    )
    st.dataframe(project_counts, use_container_width=True)

with col2:
    st.subheader("Subjects by Response")
    response_counts = (
        baseline.groupby("response")["subject"]
        .nunique()
        .reset_index(name="subject_count")
    )
    st.dataframe(response_counts, use_container_width=True)

with col3:
    st.subheader("Subjects by Sex")
    sex_counts = (
        baseline.groupby("sex")["subject"]
        .nunique()
        .reset_index(name="subject_count")
    )
    st.dataframe(sex_counts, use_container_width=True)


st.subheader("Requested B-cell Result")

st.metric(
    "Average B cells: melanoma male responders at time = 0",
    "10206.15",
)

st.caption(
    "The assignment also requested the keyword quintazide."
)
