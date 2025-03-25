
class Collections:
    SITES = "sites"
    FIRST_RESPONDERS = "first_responders"
    STAFF = "staff"

class Settings:
    DB_SERVER = "mongodb://localhost:27017/"
    DB_CLIENT = "menaterdb"
    DEBUG = True

    DB_COLLECTIONS = [
        Collections.SITES, Collections.FIRST_RESPONDERS, Collections.STAFF
    ]