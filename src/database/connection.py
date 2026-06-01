import os
from pathlib import Path

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path)

if not dotenv_path.exists():
    raise FileNotFoundError(f"Missing .env file at {dotenv_path}")


def _build_connection_config(include_database=True) -> dict:
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
    }
    if include_database:
        config['database'] = os.getenv('MYSQL_DATABASE', 'sisfarma')
    return config


def _connect_with_plugin_config(config: dict):
    supplied_plugin = os.getenv('MYSQL_AUTH_PLUGIN')
    auth_plugins = [supplied_plugin] if supplied_plugin else [None, 'mysql_native_password', 'caching_sha2_password']

    last_error = None
    for plugin in auth_plugins:
        connection_params = config.copy()
        if plugin:
            connection_params['auth_plugin'] = plugin
        try:
            return mysql.connector.connect(**connection_params)
        except Error as err:
            last_error = err
            continue

    raise last_error


def get_connection():
    return _connect_with_plugin_config(_build_connection_config(include_database=True))


def get_server_connection():
    return _connect_with_plugin_config(_build_connection_config(include_database=False))


def execute_query(query: str, params=None, fetch_one=False, fetch_all=False):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        conn.commit()
    except Error:
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
