from geweb import log
from geweb.db.pgsql.psycopg2_pool import PostgresConnectionPool
from datetime import datetime

import settings

def fetchone(q, subs=None, default=None):
    pool = PostgresConnectionPool(**settings.db)
    res = pool.fetchone(q, subs)
    return res

def fetchall(q, subs=None):
    pool = PostgresConnectionPool(**settings.db)
    res = pool.fetchall(q, subs)
    return res

def perform(q, subs=None):
    """
    Executes the query, returns nothing
    """
    pool = PostgresConnectionPool(**settings.db)
    pool.execute(q, subs)

