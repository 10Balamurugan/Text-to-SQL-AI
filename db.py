import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key, default)
    if v is None:
        return None
    s = str(v).strip().strip('"').strip("'")
    return s if s else None


def get_connection():
    """Create and return a MySQL connection."""
    host = _env("DB_HOST", "localhost") or "localhost"
    port_raw = _env("DB_PORT", "3306") or "3306"
    user = _env("DB_USER")
    password = _env("DB_PASSWORD")
    database = _env("DB_NAME")
    return mysql.connector.connect(
        host=host,
        port=int(port_raw),
        user=user,
        password=password,
        database=database,
    )


def get_schema() -> str:
    """
    Fetch all table names and their columns from the connected MySQL database.
    Returns a formatted string to inject into the LLM prompt.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []
    for table in tables:
        cursor.execute(f"DESCRIBE `{table}`;")
        columns = cursor.fetchall()
        col_defs = ", ".join(
            f"{col[0]} ({col[1]})" for col in columns
        )
        schema_parts.append(f"Table `{table}`: {col_defs}")

    cursor.close()
    conn.close()

    return "\n".join(schema_parts)


def run_query(sql: str) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a DataFrame.
    Raises an exception if the query fails.
    """
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn)
    finally:
        conn.close()
    return df


def test_connection() -> bool:
    """Return True if DB connection succeeds, False otherwise."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False
