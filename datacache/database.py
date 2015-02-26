import sqlite3

from typechecks import require_integer

METADATA_COLUMN_NAME = "_datacache_metadata"

class Database(object):
    """
    Wrapper object for sqlite3 database which provides helpers for
    querying and constructing the datacache metadata table, as well as
    creating and checking for existence of particular table names.
    """
    def __init__(self, path):
        self.path = path
        self.connection = sqlite3.connect(path)

    def close(self):
        self.connection.commit()
        self.connection.close()

    def has_table(self, table_name):
        """Does a table named `table_name` exist in the sqlite database?"""
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='%s'""" % table_name
        cursor = self.connection.execute(query)
        results = cursor.fetchmany()
        return len(results) > 0

    def execute_sql(self, sql, commit=False):
        logging.info("Running sqlite query: \"%s\"", sql)
        self.connection.execute(sql)
        if commit:
            self.connection.commit()

    def has_tables(self, table_names):
        """Are all of the given table names present in the database?"""
        return all(db_has_table(db, table_name) for table_name in table_names)

    def has_version(self):
        return self.has_table(METADATA_COLUMN_NAME)

    def version(self):
        query =  "SELECT version FROM %s" % METADATA_COLUMN_NAME
        cursor = db.execute(query)
        version = cursor.fetchone()
        if not version:
            return 0
        else:
            return int(version[0])

    def set_version(version):
        """
        Create metadata table for database with version number.

        Parameters
        ----------
        version : int
            Tag created database with user-specified version number
        """
        require_integer(version, "version")
        create_metadata_sql = \
            "CREATE TABLE %s (version INT)" % METADATA_COLUMN_NAME
        self.execute_sql(create_metadata_sql)
        insert_version_sql = \
            "INSERT INTO %s VALUES (%s)" % (METADATA_COLUMN_NAME, version)
        self.execute_sql(insert_version_sql)

    def create_table(self, table_name, column_types, primary=None, nullable=()):
        """Creates a sqlite3 table from the given metadata.

        Parameters
        ----------

        column_types : list of (str, str) pairs
            First element of each tuple is the column name, second element is the sqlite3 type

        primary : str, optional
            Which column is the primary key

        nullable : iterable, optional
            Names of columns which have null values
        """
        require_string(table_name, "table name")
        require_iterable_of(column_types, tuple, name="rows")
        if primary is not None:
            require_string(primary, "primary")
        require_iterable_of(nullable, str, name="nullable")

        column_decls = []
        for column_name, column_type in col_types:
            decl = "%s %s" % (col_name,t)
            if column_name == primary:
                decl += " UNIQUE PRIMARY KEY"
            if column_name not in nullable:
                decl += " NOT NULL"
            column_decls.append(decl)
        column_decl_str = ", ".join(column_decls)
        create_table_sql = \
            "CREATE TABLE %s (%s)" % (table_name, col_decl_str)
        self.execute_sql(db, create_table_sql)