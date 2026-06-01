import os
from pathlib import Path
from .connection import get_connection, get_server_connection


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
            cursor.execute(stmt)
        connection.commit()
    finally:
        cursor.close()
        if connection.is_connected():
            connection.close()


if __name__ == '__main__':
    init_database()
    print('Database schema executed successfully.')
