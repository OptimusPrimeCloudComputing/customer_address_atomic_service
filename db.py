import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = os.getenv("DB_USER", "myapp_user")
DB_PASS = os.getenv("DB_PASS", "Password_123")
DB_NAME = os.getenv("DB_NAME", "addresses")
DB_HOST = os.getenv("DB_HOST", "34.10.129.69") #34.10.129.69   34.171.164.80
DB_PORT = os.getenv("DB_PORT", "3306")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"Using local connection via {DB_HOST}:{DB_PORT}")


CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()