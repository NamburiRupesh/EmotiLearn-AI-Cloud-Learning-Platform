import os
from urllib.parse import urlparse, unquote
import mysql.connector
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()


def _clean_val(val, default=""):
    """Strip quotes and whitespace from env values."""
    if val is None:
        return default
    s = str(val).strip()
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1].strip()
    return s


def get_db_config():
    """Build a MySQL connection configuration dictionary supporting:
    - DATABASE_URL / MYSQL_URL connection strings
    - MYSQL_* environment variables
    - DB_* environment variables (standard TiDB/Cloud export)
    """
    database_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")

    if database_url:
        parsed = urlparse(database_url)
        config = {
            "host": parsed.hostname or "localhost",
            "port": int(parsed.port) if parsed.port else 3306,
            "user": unquote(parsed.username) if parsed.username else "root",
            "password": unquote(parsed.password) if parsed.password else "",
            "database": parsed.path.lstrip("/") if parsed.path else "emotilearn_db",
        }
        query_str = (parsed.query or "").lower()
        if "ssl=false" in query_str or "ssl_mode=disabled" in query_str:
            config["ssl_disabled"] = True
        elif config["host"] not in ("localhost", "127.0.0.1"):
            config["ssl_disabled"] = False
        return config

    # Support both MYSQL_* and DB_* variable names
    host = _clean_val(os.getenv("MYSQL_HOST") or os.getenv("DB_HOST"), "localhost")
    port_val = _clean_val(os.getenv("MYSQL_PORT") or os.getenv("DB_PORT"), "3306")
    port = int(port_val) if port_val.isdigit() else 3306
    user = _clean_val(os.getenv("MYSQL_USER") or os.getenv("DB_USERNAME") or os.getenv("DB_USER"), "root")
    password = _clean_val(os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD"), "")
    database = _clean_val(os.getenv("MYSQL_DATABASE") or os.getenv("DB_DATABASE"), "emotilearn_db")

    # SSL configuration: Default to True if remote cloud host or if explicitly requested
    ssl_env = _clean_val(os.getenv("MYSQL_SSL") or os.getenv("DB_SSL"), "").lower()
    if ssl_env in ("false", "0", "no"):
        ssl_disabled = True
    elif ssl_env in ("true", "1", "yes"):
        ssl_disabled = False
    else:
        # Auto-detect: if connecting to a remote host (e.g. tidbcloud, aiven, aws), enable SSL
        ssl_disabled = host in ("localhost", "127.0.0.1")

    config = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "ssl_disabled": ssl_disabled,
    }

    ssl_ca = os.getenv("MYSQL_SSL_CA")
    if ssl_ca and os.path.exists(ssl_ca):
        config["ssl_ca"] = ssl_ca

    return config


def get_db_connection():
    """Create and return a new MySQL connection.
    Automatically handles cloud SSL, custom ports, and timeouts.
    """
    config = get_db_config()
    connection = mysql.connector.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        ssl_disabled=config.get("ssl_disabled", False),
        connect_timeout=15,
        autocommit=False,
    )
    return connection


def test_connection():
    """Diagnostic helper to verify database connectivity from the CLI."""
    config = get_db_config()
    print("--------------------------------------------------")
    print("Testing EmotiLearn Database Connection...")
    print(f"Host     : {config['host']}")
    print(f"Port     : {config['port']}")
    print(f"User     : {config['user']}")
    print(f"Database : {config['database']}")
    print(f"SSL Disabled: {config.get('ssl_disabled', False)}")
    print("--------------------------------------------------")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION(), CURRENT_TIMESTAMP();")
        row = cursor.fetchone()
        print(f"[SUCCESS] Connected to MySQL.")
        print(f"Version  : {row[0]}")
        print(f"DB Time  : {row[1]}")

        cursor.execute("SHOW TABLES;")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables ({len(tables)}): {', '.join(tables) if tables else 'None yet'}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[FAILED] Connection Failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
