import os
from dotenv import load_dotenv
load_dotenv()

# --- Config ---
def get_database_url():
    db_mode = os.getenv("DB_MODE", "development")
    
    if db_mode == "development":
        # Use SQLite for local development
        return os.getenv("SQLITE_URL", "sqlite:///testdb.sqlite3")
    else:
        # Use MySQL for production
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        host = os.getenv("MYSQL_HOST")
        port = os.getenv("MYSQL_PORT")
        db = os.getenv("MYSQL_DB")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"