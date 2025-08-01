from pymongo import MongoClient

from settings import Settings, Collections


def setup_indexes(db):
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]
    recommended_natars_collection.create_index('id', unique=True)

def setup_collections(db):
    for collection in Settings.DB_COLLECTIONS:
        db[collection]

def run_setup():
    client = MongoClient(Settings.DB_SERVER)
    db = client[Settings.DB_CLIENT]

    setup_collections(db)
    setup_indexes(db)

if __name__ == '__main__':
    run_setup()
