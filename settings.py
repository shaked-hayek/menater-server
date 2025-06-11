
class Collections:
    SITES = "sites"
    FIRST_RESPONDERS = "first_responders"
    STAFF = "staff"

class Settings:
    DB_SERVER = "mongodb://localhost:27017/"
    DB_CLIENT = "menaterdb"
    DEBUG = True

    DB_COLLECTIONS = [
        Collections.SITES, 
        Collections.FIRST_RESPONDERS, 
        Collections.STAFF,
        Collections.RECOMMENDED_NATARS,
        Collections.LOG,
    ]

class ArcgisSettings:
    SERVER_URL = 'https://menater-server.localdomain:6443/arcgis'
    PORTAL_URL = 'https://menater-server.localdomain/portal'
    USERNAME = 'admin'
    PASSWORD = 'Password1'
