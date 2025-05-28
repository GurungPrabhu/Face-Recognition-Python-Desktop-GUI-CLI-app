from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
import os
from .config import DB_PATH

Base = declarative_base()


class Database:
    def __init__(self, db_path=None):
        """Initialize the database connection and create tables if necessary."""
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = DB_PATH
        self._ensure_db_exists()
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self._init_db()

    def _ensure_db_exists(self):
        """Ensure the database file exists at the specified path."""
        db_dir = os.path.dirname(self.db_path)
        # Ensure the directory exists
        os.makedirs(db_dir, exist_ok=True)

        # Create the database file if it doesn't exist
        if not os.path.exists(self.db_path):
            print(f"Creating new SQLite database at {self.db_path}...")
            # Create the empty database
            open(self.db_path, "w").close()

    def _init_db(self):
        """Initialize the database and create tables if necessary."""
        print(f"Connecting to database at {self.db_path}")
        Base.metadata.create_all(self.engine)
        print("INFO: Database initialized")

    def get_session(self):
        """Return a new SQLAlchemy session."""
        return self.Session()

    def close_connection(self):
        """Closes the session factory (optional in SQLAlchemy, for cleanup)."""
        self.Session.remove()
        print("INFO: SQLAlchemy session closed.")

    def create(self, model):
        """Create a new record in the database."""
        session = self.get_session()
        session.add(model)
        session.commit()
        session.close()

    def get_all(self, model):
        """Fetch all records from the database."""
        session = self.get_session()
        records = session.query(model).all()
        session.close()
        return records

    def update(self, model):
        """Update an existing record in the database."""
        session = self.get_session()
        session.merge(model)
        session.commit()
        session.close()

    def find(self, model, **kwargs):
        """
        Find a record in the database based on dynamic filters.

        Args:
            model: The model class to query.
            **kwargs: Key-value pairs representing the filter criteria.

        Returns:
            The first record matching the criteria, or None if no match is found.
        """
        session = self.get_session()
        record = session.query(model).filter_by(**kwargs).first()
        session.close()
        return record

    def find_all(self, model, *, options=None, **filters):
        session = self.get_session()
        query = session.query(model)

        if options:
            for opt in options:
                query = query.options(opt)

        return query.filter_by(**filters).all()
