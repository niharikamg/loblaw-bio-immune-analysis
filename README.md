# Loblaw Bio Immune Cell Analysis

A reproducible Python and SQLite workflow for analyzing immune cell populations in a clinical trial, including statistical comparisons and an interactive Streamlit dashboard.

## Quick Links

- [Summary Table](summary_table.csv)
- [Statistical Results](statistical_results.csv)
- [Responder Boxplots](responder_boxplots.png)
- [Baseline Miraclib Subset](baseline_miraclib_subset.csv)

## Project Overview

This project analyzes immune cell counts for five populations:

- B cells
- CD8 T cells
- CD4 T cells
- NK cells
- Monocytes

The workflow covers data loading, relational database design, relative-frequency calculations, responder versus non-responder comparisons, subset analysis, and dashboard visualization.

## Project Structure

```text
.
├── cell-count.csv
├── load_data.py
├── analysis.py
├── statistics_analysis.py
├── subset_analysis.py
├── dashboard.py
├── requirements.txt
├── Makefile
├── cell_count.db
├── summary_table.csv
├── statistical_results.csv
├── responder_boxplots.png
└── baseline_miraclib_subset.csv




