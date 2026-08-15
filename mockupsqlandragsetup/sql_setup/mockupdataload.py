from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().with_name("mockup_data.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE vendor (
    vendor_agreement_number TEXT NOT NULL,
    vendor_number TEXT NOT NULL,
    agreement_create_date TEXT NOT NULL,
    vendor_name TEXT NOT NULL,
    vendor_addr_country TEXT NOT NULL,
    vendor_addr_state TEXT NOT NULL,
    vendor_type TEXT NOT NULL CHECK (vendor_type IN ('big', 'small')),
    update_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_userid TEXT NOT NULL,
    CONSTRAINT pk_vendor PRIMARY KEY (vendor_agreement_number)
);

CREATE TABLE agreement (
    vendor_agreement_number TEXT NOT NULL,
    agreement_type TEXT NOT NULL,
    agreement_status TEXT NOT NULL,
    agreement_eff_date TEXT NOT NULL,
    agreement_exp_date TEXT NOT NULL,
    number_of_items INTEGER NOT NULL DEFAULT 0,
    last_updated_by TEXT NOT NULL,
    update_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_agreement PRIMARY KEY (vendor_agreement_number, agreement_type),
    CONSTRAINT fk_agreement_vendor FOREIGN KEY (vendor_agreement_number)
        REFERENCES vendor(vendor_agreement_number) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE purchase_details (
    vendor_agreement_number TEXT NOT NULL,
    purchase_id TEXT NOT NULL,
    purchase_type TEXT NOT NULL,
    purchase_date TEXT NOT NULL,
    purchase_update_date TEXT,
    number_of_items INTEGER NOT NULL DEFAULT 0,
    last_updated_by TEXT NOT NULL,
    update_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_purchase_details PRIMARY KEY (vendor_agreement_number, purchase_id, purchase_type, purchase_date),
    CONSTRAINT fk_purchase_vendor FOREIGN KEY (vendor_agreement_number)
        REFERENCES vendor(vendor_agreement_number) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE item_receiving_details (
    vendor_agreement_number TEXT NOT NULL,
    purchase_id TEXT NOT NULL,
    purchase_type TEXT NOT NULL,
    purchase_date TEXT NOT NULL,
    item_number TEXT NOT NULL,
    item_cost NUMERIC(15,4) NOT NULL,
    item_ordered INTEGER NOT NULL DEFAULT 0,
    item_received INTEGER NOT NULL DEFAULT 0,
    item_sold INTEGER NOT NULL DEFAULT 0,
    item_brokerage_percentage NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    item_brokerage_cost NUMERIC(15,4) NOT NULL DEFAULT 0.0000,
    last_update_by TEXT NOT NULL,
    update_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_item_receiving_details PRIMARY KEY (vendor_agreement_number, purchase_id, purchase_type, item_number, item_cost),
    CONSTRAINT fk_item_rec_purchase_details FOREIGN KEY (vendor_agreement_number, purchase_id, purchase_type, purchase_date)
        REFERENCES purchase_details(vendor_agreement_number, purchase_id, purchase_type, purchase_date) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE UNIQUE INDEX uq_item_rec_composite
    ON item_receiving_details (vendor_agreement_number, purchase_id, purchase_type, item_number, item_cost);

CREATE TABLE receiving_history (
    vendor_agreement_number TEXT NOT NULL,
    purchase_id TEXT NOT NULL,
    purchase_type TEXT NOT NULL,
    item_number TEXT NOT NULL,
    item_cost NUMERIC(15,4) NOT NULL,
    activity_date TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    item_ordered INTEGER NOT NULL DEFAULT 0,
    item_received INTEGER NOT NULL DEFAULT 0,
    item_sold INTEGER NOT NULL DEFAULT 0,
    brokerage_cost NUMERIC(15,4) NOT NULL DEFAULT 0.0000,
    last_update_by TEXT NOT NULL,
    update_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_receiving_history PRIMARY KEY (vendor_agreement_number, purchase_id, purchase_type, item_number, item_cost, activity_date, sequence),
    CONSTRAINT fk_history_item_details FOREIGN KEY (vendor_agreement_number, purchase_id, purchase_type, item_number, item_cost)
        REFERENCES item_receiving_details(vendor_agreement_number, purchase_id, purchase_type, item_number, item_cost) ON DELETE RESTRICT ON UPDATE CASCADE
);
"""


def build_mock_data():
    vendors = []
    agreements = []
    purchase_details = []
    item_receiving_details = []
    receiving_history = []

    vendor_names = [
        "Alpha Foods Group",
        "Blue Harbor Supply",
        "Central Market Imports",
        "Delta Logistics Co",
        "Evergreen Retailers",
        "Forest Valley Goods",
        "Golden Point Traders",
        "Harborline Distributors",
        "Iron Oak Wholesale",
        "Juniper Valley Foods",
    ]

    countries = [
        "USA",
        "Canada",
        "Mexico",
        "USA",
        "UK",
        "Germany",
        "USA",
        "India",
        "Australia",
        "USA",
    ]

    states = [
        "Texas",
        "Ontario",
        "Jalisco",
        "California",
        "England",
        "Bavaria",
        "Florida",
        "Maharashtra",
        "New South Wales",
        "Illinois",
    ]

    types = ["big", "small", "big", "small", "big", "small", "big", "small", "big", "small"]
    base_dates = [
        "2023-01-15",
        "2023-02-12",
        "2023-03-08",
        "2023-04-17",
        "2023-05-22",
        "2023-06-10",
        "2023-07-30",
        "2023-08-05",
        "2023-09-12",
        "2023-10-19",
    ]

    for i in range(1, 11):
        vendor_number = f"VND-{i:04d}"
        vendor_agreement_number = f"AGR-{i:04d}"
        vendor_name = vendor_names[i - 1]
        agreement_create_date = base_dates[i - 1]
        vendor_addr_country = countries[i - 1]
        vendor_addr_state = states[i - 1]
        vendor_type = types[i - 1]

        vendors.append(
            (
                vendor_agreement_number,
                vendor_number,
                agreement_create_date,
                vendor_name,
                vendor_addr_country,
                vendor_addr_state,
                vendor_type,
                "2024-01-15T08:30:00",
                f"user_{i:02d}",
            )
        )

        agreements.append(
            (
                vendor_agreement_number,
                f"AGREE-{i:02d}",
                "Active",
                agreement_create_date,
                "2028-12-31",
                250 + i * 10,
                f"manager_{i:02d}",
                "2024-01-15T08:30:00",
            )
        )

        purchase_id = f"PUR-{i:04d}"
        purchase_type = "regular" if i % 2 == 0 else "bulk"
        purchase_date = f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
        purchase_update_date = f"2024-{(i % 12) + 1:02d}-{(i % 28) + 3:02d}"

        purchase_details.append(
            (
                vendor_agreement_number,
                purchase_id,
                purchase_type,
                purchase_date,
                purchase_update_date,
                30 + i,
                f"buyer_{i:02d}",
                "2024-02-01T09:00:00",
            )
        )

        item_number = f"ITEM-{i:04d}"
        item_cost = round(12.5 + i * 1.75, 4)
        item_ordered = 100 + i * 5
        item_received = 90 + i * 4
        item_sold = 60 + i * 3
        brokerage_percentage = round(2.25 + (i * 0.15), 2)
        brokerage_cost = round(item_cost * item_received * (brokerage_percentage / 100), 4)

        item_receiving_details.append(
            (
                vendor_agreement_number,
                purchase_id,
                purchase_type,
                purchase_date,
                item_number,
                item_cost,
                item_ordered,
                item_received,
                item_sold,
                brokerage_percentage,
                brokerage_cost,
                f"receiver_{i:02d}",
                "2024-02-02T07:45:00",
            )
        )

        receiving_history.append(
            (
                vendor_agreement_number,
                purchase_id,
                purchase_type,
                item_number,
                item_cost,
                purchase_date,
                1,
                item_ordered,
                item_received,
                item_sold,
                brokerage_cost,
                f"admin_{i:02d}",
                "2024-02-03T08:15:00",
            )
        )

    return vendors, agreements, purchase_details, item_receiving_details, receiving_history


def create_database():
    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA)

        vendors, agreements, purchase_details, item_receiving_details, receiving_history = build_mock_data()

        conn.executemany(
            """
            INSERT INTO vendor (
                vendor_agreement_number,
                vendor_number,
                agreement_create_date,
                vendor_name,
                vendor_addr_country,
                vendor_addr_state,
                vendor_type,
                update_timestamp,
                update_userid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            vendors,
        )

        conn.executemany(
            """
            INSERT INTO agreement (
                vendor_agreement_number,
                agreement_type,
                agreement_status,
                agreement_eff_date,
                agreement_exp_date,
                number_of_items,
                last_updated_by,
                update_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            agreements,
        )

        conn.executemany(
            """
            INSERT INTO purchase_details (
                vendor_agreement_number,
                purchase_id,
                purchase_type,
                purchase_date,
                purchase_update_date,
                number_of_items,
                last_updated_by,
                update_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            purchase_details,
        )

        conn.executemany(
            """
            INSERT INTO item_receiving_details (
                vendor_agreement_number,
                purchase_id,
                purchase_type,
                purchase_date,
                item_number,
                item_cost,
                item_ordered,
                item_received,
                item_sold,
                item_brokerage_percentage,
                item_brokerage_cost,
                last_update_by,
                update_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            item_receiving_details,
        )

        conn.executemany(
            """
            INSERT INTO receiving_history (
                vendor_agreement_number,
                purchase_id,
                purchase_type,
                item_number,
                item_cost,
                activity_date,
                sequence,
                item_ordered,
                item_received,
                item_sold,
                brokerage_cost,
                last_update_by,
                update_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            receiving_history,
        )

        conn.commit()

        print(f"SQLite database created at: {DB_PATH}")
        for table_name in [
            "vendor",
            "agreement",
            "purchase_details",
            "item_receiving_details",
            "receiving_history",
        ]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"{table_name}: {count} rows")


if __name__ == "__main__":
    create_database()
