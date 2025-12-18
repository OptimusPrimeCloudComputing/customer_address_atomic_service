# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
#
# DB_USER = os.getenv("DB_USER", "myapp_user")
# DB_PASS = os.getenv("DB_PASS", "Password_123")
# DB_NAME = os.getenv("DB_NAME", "addresses")
# DB_HOST = os.getenv("DB_HOST", "34.10.129.69") #34.10.129.69   34.171.164.80
# DB_PORT = os.getenv("DB_PORT", "3306")
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# print(f"Using local connection via {DB_HOST}:{DB_PORT}")
#
#
# CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")
#
# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
# )
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Define constants for connection details
db_user = os.environ.get("MYSQL_USER", "myapp_user")
db_pass = os.environ.get("MYSQL_PASSWORD", "Password_123")
db_name = os.environ.get("MYSQL_DB", "addresses")
db_host = os.environ.get("MYSQL_HOST", "34.10.129.69")
db_port = int(os.environ.get("MYSQL_PORT", 3306))
connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

# DETECT WINDOWS (Force TCP)
if os.name == 'nt':
    print("--- DETECTED WINDOWS: Ignoring Unix Socket configuration ---")
    connection_name = None

# BUILD THE URL OBJECT SAFELY
# This method automatically handles special characters like '@' in passwords
if connection_name:
    # Cloud Run (Unix Socket)
    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_pass,
        database=db_name,
        query={"unix_socket": f"/cloudsql/{connection_name}"}
    )

else:
    # Local (TCP)
    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
        database=db_name
    )

# CREATE ENGINE
engine = create_engine(connection_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    try:
        print(f"--- ATTEMPTING CONNECTION TO: {db_host} ---")
        with engine.connect() as connection:
            print(f"--- SUCCESS: Connected to database '{db_name}' ---")
    except Exception as e:
        print(f"--- FAILURE: Could not connect ---")
        print(f"Error: {e}")