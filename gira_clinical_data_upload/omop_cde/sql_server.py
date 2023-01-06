from configparser import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def sql_server_engine(config_file='config.ini'):
    # Read config file
    parser = ConfigParser(inline_comment_prefixes=['#'])
    parser.read(config_file)

    # SqlAlchemy
    connection_url = URL.create(
        "mssql+pyodbc",
        username=parser.get('OMOP', 'DB_USER'),
        password=parser.get('OMOP', 'DB_PASS'),
        host=parser.get('OMOP', 'DB_URL'),
        database=parser.get('OMOP', 'DB_NAME'),
        query={
            "driver": parser.get('OMOP', 'DB_DRIVER')
        },
    )
    engine = create_engine(connection_url)
    return engine


def compare_databases(a, b):
    """ Compares the names of two databases to determine if they're the same or which one is newer.

    Returns
    -------
    0 - databases are the same
    1 - a is newer
    -1 - b is newer
    """
    # For CUIMC OMOP naming structure, can rely on string comparisons to determine which one's newer
    a = a.lower()
    b = b.lower()
    if a == b:
        return 0
    return 1 if a > b else -1
