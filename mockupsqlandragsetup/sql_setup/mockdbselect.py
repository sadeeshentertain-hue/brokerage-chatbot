import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().with_name("mockup_data.db")

TABLES = [
    "vendor",
    "agreement",
    "purchase_details",
    "item_receiving_details",
    "receiving_history",
]


def fetch_all(table_name: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        columns = [
            col[0] for col in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]
        rows = conn.execute(f"SELECT * FROM {table_name} ORDER BY 1").fetchall()
        return columns, rows


def print_table(table_name: str, columns, rows):
    print(f"\n=== {table_name.upper()} ===")

    if not rows:
        print("No records found.")
        return

    widths = [len(str(column)) for column in columns]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(str(value)))

    header = " | ".join(str(column).ljust(widths[idx]) for idx, column in enumerate(columns))
    separator = "-+-".join("-" * width for width in widths)

    print(header)
    print(separator)

    for row in rows:
        print(" | ".join(str(value).ljust(widths[idx]) for idx, value in enumerate(row)))


def main():
    for table_name in TABLES:
        columns, rows = fetch_all(table_name)
        print_table(table_name, columns, rows)


if __name__ == "__main__":
    main()
