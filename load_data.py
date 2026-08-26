import csv
import sqlite3
from pathlib import Path

CSV_FILE = Path("cell-count.csv")
DB_FILE = Path("cell_count.db")

POPULATIONS = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]


def create_database(connection):
    """Create tables for sample metadata and cell counts."""

    connection.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            sample_id TEXT PRIMARY KEY,
            project TEXT,
            subject TEXT,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT,
            sample_type TEXT,
            time_from_treatment_start INTEGER
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS cell_counts (
            sample_id TEXT NOT NULL,
            population TEXT NOT NULL,
            count INTEGER NOT NULL,
            PRIMARY KEY (sample_id, population),
            FOREIGN KEY (sample_id)
                REFERENCES samples(sample_id)
        )
    """)

    connection.commit()


def load_data(connection):
    """Load cell-count.csv into the SQLite database."""

    with CSV_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            connection.execute(
                """
                INSERT INTO samples (
                    sample_id,
                    project,
                    subject,
                    condition,
                    age,
                    sex,
                    treatment,
                    response,
                    sample_type,
                    time_from_treatment_start
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["sample"],
                    row["project"],
                    row["subject"],
                    row["condition"],
                    int(row["age"]),
                    row["sex"],
                    row["treatment"],
                    row["response"],
                    row["sample_type"],
                    int(row["time_from_treatment_start"]),
                ),
            )

            for population in POPULATIONS:
                connection.execute(
                    """
                    INSERT INTO cell_counts (
                        sample_id,
                        population,
                        count
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        row["sample"],
                        population,
                        int(row[population]),
                    ),
                )

    connection.commit()


def main():
    if DB_FILE.exists():
        DB_FILE.unlink()

    connection = sqlite3.connect(DB_FILE)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        create_database(connection)
        load_data(connection)
    finally:
        connection.close()

    print(f"Database created successfully: {DB_FILE}")


if __name__ == "__main__":
    main()
