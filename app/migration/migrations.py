from sqlalchemy import Inspector
from sqlalchemy.orm import declarative_base

from models.user import Users
from models.attendance import Attendance

Base = declarative_base()


def run_migration_table(engine):
    """Check if the 'users' and 'attendances' tables exist and create them if they don't."""
    inspector = Inspector.from_engine(engine)
    existing_tables = inspector.get_table_names()

    if "users" not in existing_tables:
        Users.__table__.create(engine, checkfirst=True)
        print("INFO: 'users' table created successfully.")

    if "attendances" not in existing_tables:
        Attendance.__table__.create(engine, checkfirst=True)
        print("INFO: 'attendances' table created successfully.")


def run_migration_down(engine):
    """Drop the 'users' and 'attendances' tables if they exist."""
    inspector = Inspector.from_engine(engine)
    existing_tables = inspector.get_table_names()

    if "attendances" in existing_tables:
        Attendance.__table__.drop(engine, checkfirst=True)
        print("INFO: 'attendances' table dropped successfully.")

    if "users" in existing_tables:
        Users.__table__.drop(engine, checkfirst=True)
        print("INFO: 'users' table dropped successfully.")
