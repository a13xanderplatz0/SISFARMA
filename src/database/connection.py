import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error, pooling

# ---------------------------------------------------------------------------
# Determine which database to connect to: 'local' or 'online'
# Priority:
#   1. Command-line argument: 'local' / '--local'  or  'online' / '--online'
#   2. Running inside Railway (MYSQLHOST is injected by the platform) → online
#   3. Default to 'online' (use .env)
# ---------------------------------------------------------------------------

_args = [a.lower().lstrip('-') for a in sys.argv[1:]]

if 'local' in _args:
    DB_MODE = 'local'
elif 'online' in _args:
    DB_MODE = 'online'
elif os.getenv('MYSQLHOST'):          # injected by Railway in production
    DB_MODE = 'online'
else:
    DB_MODE = 'online'                # default

BASE_DIR = Path(__file__).resolve().parent.parent.parent

if DB_MODE == 'local':
    env_file = BASE_DIR / '.env.example'
    load_dotenv(env_file, override=True)
else:
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)

# Read resolved values for display
_db_host = os.getenv('MYSQLHOST') or os.getenv('MYSQL_HOST', 'localhost')
_db_port = os.getenv('MYSQLPORT') or os.getenv('MYSQL_PORT', '3306')
_db_name = os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE', 'sisfarma')

_separator = '-' * 55
if DB_MODE == 'local':
    print(f"\n{_separator}")
    print(f"  [DB MODE] >>> LOCAL database (desde .env.example)")
    print(f"  Host    : {_db_host}")
    print(f"  Port    : {_db_port}")
    print(f"  Database: {_db_name}")
    print(f"{_separator}\n")
else:
    print(f"\n{_separator}")
    print(f"  [DB MODE] >>> ONLINE database (Railway Cloud)")
    print(f"  Host    : {_db_host}")
    print(f"  Port    : {_db_port}")
    print(f"  Database: {_db_name}")
    print(f"{_separator}\n")


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _build_connection_config(include_database=True) -> dict:
    # Soporta tanto variables Railway (MYSQLHOST, etc.) como variables simples (MYSQL_HOST, etc.)
    host     = os.getenv('MYSQLHOST') or os.getenv('MYSQL_HOST', 'localhost')
    port_raw = os.getenv('MYSQLPORT') or os.getenv('MYSQL_PORT')
    user     = os.getenv('MYSQLUSER') or os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQLPASSWORD') or os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE', 'sisfarma')

    config = {
        'host':     host,
        'port':     int(port_raw) if port_raw else 3306,
        'user':     user,
        'password': password,
    }
    if include_database:
        config['database'] = database
    return config


def _connect_with_plugin_config(config: dict):
    supplied_plugin = os.getenv('MYSQL_AUTH_PLUGIN')
    auth_plugins = (
        [supplied_plugin]
        if supplied_plugin
        else [None, 'mysql_native_password', 'caching_sha2_password']
    )

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


_db_pool = None

def get_connection():
    global _db_pool
    if _db_pool is None:
        config = _build_connection_config(include_database=True)
        supplied_plugin = os.getenv('MYSQL_AUTH_PLUGIN')
        auth_plugins = (
            [supplied_plugin]
            if supplied_plugin
            else [None, 'mysql_native_password', 'caching_sha2_password']
        )

        working_config = None
        last_error = None
        for plugin in auth_plugins:
            connection_params = config.copy()
            if plugin:
                connection_params['auth_plugin'] = plugin
            try:
                conn = mysql.connector.connect(**connection_params)
                conn.close()
                working_config = connection_params
                break
            except Error as err:
                last_error = err
                continue

        if working_config is None:
            raise last_error if last_error else Error("Could not connect to database")

        _db_pool = pooling.MySQLConnectionPool(
            pool_name="sisfarmapool",
            pool_size=10,
            pool_reset_session=True,
            **working_config
        )

    return _db_pool.get_connection()


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