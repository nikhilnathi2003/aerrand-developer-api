"""MongoDB access for the API's domain data (keys, quotes, errands).

Everything goes through get_db() so tests can swap in an in-memory database.
"""
from django.conf import settings

_client = None
_db_override = None


def set_db_for_tests(db):
    """Point the whole app at an in-memory (mongomock) database during tests."""
    global _db_override
    _db_override = db


def get_db():
    global _client
    if _db_override is not None:
        return _db_override
    if _client is None:
        import pymongo

        _client = pymongo.MongoClient(settings.MONGO_URL)
    # database name comes from the connection string (…/aerrand)
    return _client.get_default_database()


# Collection accessors -------------------------------------------------------

def api_keys():
    return get_db()["api_keys"]


def quotes():
    return get_db()["quotes"]


def errands():
    return get_db()["errands"]
