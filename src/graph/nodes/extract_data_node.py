import sqlite3
import os

from src.config.sqlconnections import get_db_connection

from src.graph.state.agentstate import AgentState

def run_sqlite_query(state: AgentState) -> AgentState:
    """Executes an SQL query against a local SQLite database with robust error handling.

    Args:
        db_path (str): The path to the SQLite database file.
        sql_query (str): The SQL query string to execute.
    """

    try:
        # 2. Establish connection (sets timeout to 5 seconds to handle busy/locked databases)
        sql_query = state.generated_sql
        if(not sql_query or not str(sql_query).strip()):
            print("SQL query is required.")
            state.sql_error = "SQL query is required."
            return state
        connection = get_db_connection()
        if not connection:
            print("Failed to establish database connection.")
            state.sql_error = "Failed to establish database connection."
            return state
        cursor = connection.cursor()

        # 3. Execute the query
        print("Executing query...")
        cursor.execute(sql_query)

        # 4. Fetch and display data safely
        # Note: If running INSERT/UPDATE/DELETE, remember to call connection.commit() instead
        columns = [column[0] for column in cursor.description] if cursor.description else []
        results = cursor.fetchall()

        if columns:
            results.insert(0, tuple(columns))

        if not results:
            print("Query executed successfully, but returned 0 rows.")
            return state
        else:
            print(f"\n--- Success! Retrieved {len(results) - 1} rows ---")
            for row in results:
                print(row)
            
            state.db_query_result = results
        
    # Handle syntax mistakes, missing tables, or incorrect column names
    except sqlite3.OperationalError as e:
        print(f"\nOperational Error: Issue with database or query syntax.\nDetails: {e}")
        state.sql_error = f"Operational Error: Issue with database or query syntax.\nDetails: {e}"

    # Handle data integrity violations (e.g., unique constraint failures during writes)
    except sqlite3.IntegrityError as e:
        print(f"\nIntegrity Error: Data constraints violated.\nDetails: {e}")
        state.sql_error = f"Integrity Error: Data constraints violated.\nDetails: {e}"

    # Catch-all for any other SQLite-specific anomalies
    except sqlite3.Error as e:
        print(f"\nSQLite Error: An unexpected database error occurred.\nDetails: {e}")
        state.sql_error = f"SQLite Error: An unexpected database error occurred.\nDetails: {e}"

    # Catch-all for python/system level failures
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        state.sql_error = f"Unexpected Error: {e}"

    # 5. Always close the connection, even if the query crashes mid-execution
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed cleanly.")
    return state