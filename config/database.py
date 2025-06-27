import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Turso DB config
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

db_url = f"sqlite+{TURSO_DATABASE_URL}/?secure=true"

engine = create_engine(db_url, connect_args={
                      'check_same_thread': False,
                      'auth_token': TURSO_AUTH_TOKEN}, echo=True)

#Local DB config
# sqlite_file_name = "../database.sqlite"
# base_dir = os.path.dirname(os.path.realpath(__file__))
# database_url = f"sqlite:///{os.path.join(base_dir, sqlite_file_name)}"
# engine = create_engine(database_url, echo=True)


class Base(DeclarativeBase):
    pass


Session = sessionmaker(bind=engine)
