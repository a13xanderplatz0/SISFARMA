import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

# ---------------------------------------------------------------------------
# Determine which MongoDB to connect to: 'local' or 'online'
# Priority:
#   1. Command-line argument: 'local' / '--local'  or  'online' / '--online'
#   2. Running inside Railway (MONGOHOST is injected by the platform) → online
#   3. Default to 'online' (use .env)
# ---------------------------------------------------------------------------

_args = [a.lower().lstrip('-') for a in sys.argv[1:]]

if 'local' in _args:
    MONGO_MODE = 'local'
elif 'online' in _args:
    MONGO_MODE = 'online'
elif os.getenv('MONGOHOST'):          # injected by Railway in production
    MONGO_MODE = 'online'
else:
    MONGO_MODE = 'online'             # default

BASE_DIR = Path(__file__).resolve().parent.parent.parent

if MONGO_MODE == 'local':
    env_file = BASE_DIR / '.env.example'
    load_dotenv(env_file, override=True)
else:
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)

# Read resolved values for display
_mongo_host = os.getenv('MONGOHOST', 'localhost')
_mongo_port = os.getenv('MONGOPORT', '27017')
_mongo_db   = os.getenv('MONGO_DATABASE', 'sisfarma_mongo')

_separator = '-' * 55
if MONGO_MODE == 'local':
    print(f"\n{_separator}")
    print(f"  [MONGO MODE] >>> LOCAL MongoDB (desde .env.example)")
    print(f"  Host    : {_mongo_host}")
    print(f"  Port    : {_mongo_port}")
    print(f"  Database: {_mongo_db}")
    print(f"{_separator}\n")
else:
    print(f"\n{_separator}")
    print(f"  [MONGO MODE] >>> ONLINE MongoDB (Railway Cloud)")
    print(f"  Host    : {_mongo_host}")
    print(f"  Port    : {_mongo_port}")
    print(f"  Database: {_mongo_db}")
    print(f"{_separator}\n")


# ---------------------------------------------------------------------------
# Singleton client — se reutiliza en toda la app (MongoClient es thread-safe)
# ---------------------------------------------------------------------------

_client: MongoClient | None = None


def _build_mongo_uri() -> str:
    """
    Construye la URI de conexión a MongoDB.
    Soporta:
      - MONGO_URL / MONGO_PUBLIC_URL  (variable completa de Railway)
      - Variables individuales: MONGOHOST, MONGOPORT, MONGOUSER, MONGOPASSWORD
    """
    # Si Railway inyecta la URL completa, úsala directamente
    mongo_url = os.getenv('MONGO_URL') or os.getenv('MONGO_PUBLIC_URL')
    if mongo_url:
        return mongo_url

    # Construir URI desde partes individuales
    host     = os.getenv('MONGOHOST', 'localhost')
    port     = os.getenv('MONGOPORT', '27017')
    user     = os.getenv('MONGOUSER') or os.getenv('MONGO_USER', '')
    password = os.getenv('MONGOPASSWORD') or os.getenv('MONGO_PASSWORD', '')

    if user and password:
        return f"mongodb://{user}:{password}@{host}:{port}"
    return f"mongodb://{host}:{port}"


def get_client() -> MongoClient:
    """Devuelve el cliente MongoDB singleton (conexión lazy)."""
    global _client
    if _client is None:
        uri = _build_mongo_uri()
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Verificar conectividad al crear el cliente
        try:
            _client.admin.command('ping')
            print("[MongoDB] Conexión exitosa.")
        except (ConnectionFailure, ConfigurationError) as exc:
            print(f"[MongoDB] ERROR de conexión: {exc}")
            _client = None
            raise
    return _client


def get_db(db_name: str | None = None):
    """
    Devuelve la base de datos MongoDB.
    Si no se especifica db_name, usa MONGO_DATABASE del entorno.
    """
    name = db_name or os.getenv('MONGO_DATABASE', 'sisfarma_mongo')
    return get_client()[name]


def get_collection(collection_name: str, db_name: str | None = None):
    """Atajo para obtener una colección directamente."""
    return get_db(db_name)[collection_name]


def close_connection():
    """Cierra el cliente MongoDB (útil en teardown / tests)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        print("[MongoDB] Conexión cerrada.")
