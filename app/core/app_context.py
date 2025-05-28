from . import Database


class AppContext:
    def __init__(self, db_path=None):
        databaseInstance = Database(db_path)
        self.db = databaseInstance

    def get_db(self):
        """Return the database object."""
        return self.db
