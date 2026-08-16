import sqlite3
import os


def get_db_connection():
    """Establishes a connection to the SQLite database.

    Args:
        db_path (str): The path to the SQLite database file.
        sql_query (str): The SQL query string to execute.
    """
    # 1. Check if the database file actually exists before trying to connect
    db_path = "C:\\Users\\sadee\\OneDrive\\Projects\\chatbot\\brokerage-chatbot\\mockup_sql_ragsetup\\sql_setup\\mockup_data.db"
    if not os.path.exists(db_path):
        print(f"Error: The database file at '{db_path}' was not found.")
        return

    connection = None

    try:
        # 2. Establish connection (sets timeout to 5 seconds to handle busy/locked databases)
        connection = sqlite3.connect(db_path, timeout=5.0)
        return connection
    except sqlite3.Error as e:
        print(f"\nSQLite Error: An unexpected database error occurred.\nDetails: {e}")
        return None
    