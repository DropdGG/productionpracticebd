import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import config
import os

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        return psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            cursor_factory=RealDictCursor
            client_encoding='UTF8'
        )
    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor,
        sslmode='require'
    )
