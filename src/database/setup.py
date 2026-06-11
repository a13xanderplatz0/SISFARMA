import os
import re
from pathlib import Path
from .connection import get_connection, get_server_connection


def _ensure_column(connection, table_name, column_name, column_definition):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
            """,
            (table_name, column_name),
        )
        column_exists = cursor.fetchone()[0] > 0
        if not column_exists:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
            connection.commit()
    finally:
        cursor.close()


def _table_exists(connection, table_name):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
            """,
            (table_name,),
        )
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()


def _table_has_rows(connection, table_name):
    if not _table_exists(connection, table_name):
        return False

    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()


def _extract_table_name(statement, keyword):
    match = re.search(rf"{keyword}\s+([A-Z_][A-Z0-9_]*)", statement, re.IGNORECASE)
    return match.group(1) if match else None


def init_database():
    schema_path = Path(__file__).resolve().parent / 'schema.sql'
    if not schema_path.exists():
        raise FileNotFoundError(f'Missing schema file: {schema_path}')

    db_name = os.getenv('MYSQL_DATABASE', 'sisfarma')
    server_connection = get_server_connection()
    try:
        server_cursor = server_connection.cursor()
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        server_connection.commit()
    finally:
        server_cursor.close()
        if server_connection.is_connected():
            server_connection.close()

    with open(schema_path, 'r', encoding='utf-8') as schema_file:
        schema_sql = schema_file.read()

    connection = get_connection()
    try:
        cursor = connection.cursor()
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        for stmt in statements:
            normalized_stmt = stmt.strip()

            if normalized_stmt.upper().startswith('CREATE TABLE '):
                table_name = _extract_table_name(normalized_stmt, 'CREATE TABLE(?: IF NOT EXISTS)?')
                if table_name and _table_exists(connection, table_name):
                    continue
                normalized_stmt = re.sub(r'^CREATE TABLE\s+', 'CREATE TABLE IF NOT EXISTS ', normalized_stmt, flags=re.IGNORECASE)

            elif normalized_stmt.upper().startswith('INSERT INTO '):
                table_name = _extract_table_name(normalized_stmt, 'INSERT INTO')
                if table_name and _table_has_rows(connection, table_name):
                    continue

            cursor.execute(normalized_stmt)
        connection.commit()
        _ensure_column(connection, 'MEDICAMENTO', 'activo', 'activo BOOLEAN NOT NULL DEFAULT TRUE')
        _ensure_column(connection, 'PROVEEDOR', 'activo', 'activo BOOLEAN NOT NULL DEFAULT TRUE')
    finally:
        cursor.close()
        if connection.is_connected():
            connection.close()


if __name__ == '__main__':
    init_database()
    print('Database schema executed successfully.')
