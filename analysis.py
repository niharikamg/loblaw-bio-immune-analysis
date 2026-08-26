import csv
import sqlite3
from pathlib import Path

DB_FILE = Path("cell_count.db")
OUTPUT_FILE = Path("summary_table.csv")


def create_summary_table():
    """Calculate relative frequency of each cell population per sample."""

    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row

    query = """
        SELECT
            c.sample_id AS sample,
            totals.total_count,
            c.population,
            c.count,
            ROUND(
                (100.0 * c.count / totals.total_count),
                4
            ) AS percentage
        FROM cell_counts AS c
        JOIN (
            SELECT
                sample_id,
                SUM(count) AS total_count
            FROM cell_counts
            GROUP BY sample_id
        ) AS totals
            ON c.sample_id = totals.sample_id
        ORDER BY c.sample_id, c.population
    """

    rows = connection.execute(query).fetchall()
    connection.close()

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "sample",
            "total_count",
            "population",
            "count",
            "percentage",
        ])

        for row in rows:
            writer.writerow([
                row["sample"],
                row["total_count"],
                row["population"],
                row["count"],
                row["percentage"],
            ])

    print(f"Summary table created: {OUTPUT_FILE}")
    print(f"Number of rows: {len(rows)}")

    print("\nFirst 10 rows:")
    for row in rows[:10]:
        print(
            row["sample"],
            row["total_count"],
            row["population"],
            row["count"],
            row["percentage"],
        )


if __name__ == "__main__":
    create_summary_table()
