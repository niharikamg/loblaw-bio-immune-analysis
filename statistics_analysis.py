import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import mannwhitneyu


DB_FILE = Path("cell_count.db")
STATS_FILE = Path("statistical_results.csv")
PLOT_FILE = Path("responder_boxplots.png")

POPULATION_ORDER = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]


def load_analysis_data():
    """Load melanoma, miraclib, PBMC responder data from SQLite."""

    connection = sqlite3.connect(DB_FILE)

    query = """
        SELECT
            s.sample_id AS sample,
            s.subject,
            s.response,
            c.population,
            c.count,
            totals.total_count,
            100.0 * c.count / totals.total_count AS percentage
        FROM samples AS s
        JOIN cell_counts AS c
            ON s.sample_id = c.sample_id
        JOIN (
            SELECT
                sample_id,
                SUM(count) AS total_count
            FROM cell_counts
            GROUP BY sample_id
        ) AS totals
            ON s.sample_id = totals.sample_id
        WHERE LOWER(s.condition) = 'melanoma'
          AND LOWER(s.treatment) = 'miraclib'
          AND UPPER(s.sample_type) = 'PBMC'
          AND LOWER(s.response) IN ('yes', 'no')
    """

    df = pd.read_sql_query(query, connection)
    connection.close()

    return df


def benjamini_hochberg(p_values):
    """Return Benjamini-Hochberg FDR-adjusted p-values."""

    p_values = pd.Series(p_values, dtype=float)

    order = p_values.sort_values().index
    ranked = p_values.loc[order]

    adjusted = ranked * len(ranked) / range(1, len(ranked) + 1)

    # Enforce monotonic adjusted p-values from largest rank backwards.
    adjusted = adjusted.iloc[::-1].cummin().iloc[::-1]
    adjusted = adjusted.clip(upper=1.0)

    result = pd.Series(index=p_values.index, dtype=float)
    result.loc[order] = adjusted.values

    return result


def run_statistics(df):
    """Compare responder and non-responder percentages."""

    results = []

    for population in POPULATION_ORDER:
        population_df = df[df["population"] == population]

        responders = population_df.loc[
            population_df["response"].str.lower() == "yes",
            "percentage",
        ]

        non_responders = population_df.loc[
            population_df["response"].str.lower() == "no",
            "percentage",
        ]

        statistic, p_value = mannwhitneyu(
            responders,
            non_responders,
            alternative="two-sided",
        )

        results.append(
            {
                "population": population,
                "responder_n": len(responders),
                "non_responder_n": len(non_responders),
                "responder_median_percentage": responders.median(),
                "non_responder_median_percentage": non_responders.median(),
                "mann_whitney_u": statistic,
                "p_value": p_value,
            }
        )

    results_df = pd.DataFrame(results)

    results_df["adjusted_p_value"] = benjamini_hochberg(
        results_df["p_value"]
    )

    results_df["significant_raw_p"] = results_df["p_value"] < 0.05
    results_df["significant_fdr"] = results_df["adjusted_p_value"] < 0.05

    results_df.to_csv(STATS_FILE, index=False)

    return results_df


def create_boxplots(df):
    """Create responder versus non-responder boxplots."""

    fig, axes = plt.subplots(
        1,
        len(POPULATION_ORDER),
        figsize=(18, 5),
        sharey=True,
    )

    for axis, population in zip(axes, POPULATION_ORDER):
        population_df = df[df["population"] == population]

        responder_values = population_df.loc[
            population_df["response"].str.lower() == "yes",
            "percentage",
        ]

        non_responder_values = population_df.loc[
            population_df["response"].str.lower() == "no",
            "percentage",
        ]

        axis.boxplot(
            [responder_values, non_responder_values],
            tick_labels=["Responder", "Non-responder"],
        )

        axis.set_title(population.replace("_", " ").title())
        axis.tick_params(axis="x", rotation=25)

    axes[0].set_ylabel("Relative frequency (%)")

    fig.suptitle(
        "Melanoma PBMC Samples Receiving Miraclib",
        fontsize=14,
    )

    fig.tight_layout()
    fig.savefig(PLOT_FILE, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    df = load_analysis_data()

    print(f"Rows included in Part 3 analysis: {len(df)}")
    print(f"Samples included: {df['sample'].nunique()}")
    print(f"Subjects included: {df['subject'].nunique()}")

    results = run_statistics(df)
    create_boxplots(df)

    print("\nStatistical results:")
    print(results.to_string(index=False))

    print(f"\nResults saved to: {STATS_FILE}")
    print(f"Boxplot saved to: {PLOT_FILE}")


if __name__ == "__main__":
    main()
