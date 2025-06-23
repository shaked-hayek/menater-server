
class Collections:
    EVENTS = "events"
    SITES = "sites"
    STAFF = "staff"
    RECOMMENDED_NATARS = "recommended_natars"
    LOG = "actionsLog"

class Settings:
    DB_SERVER = "mongodb://localhost:27017/"
    DB_CLIENT = "menaterdb"
    DEBUG = True

    DB_COLLECTIONS = [
        Collections.EVENTS,
        Collections.SITES, 
        Collections.STAFF,
        Collections.RECOMMENDED_NATARS,
        Collections.LOG,
    ]

class ArcgisSettings:
    SERVER_URL = 'https://menater-server.localdomain:6443/arcgis'
    PORTAL_URL = 'https://menater-server.localdomain/portal'
    USERNAME = 'admin'
    PASSWORD = 'Password1'
