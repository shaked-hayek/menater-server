
class Collections:
    EVENTS = "events"
    SITES = "sites"
    STAFF = "staff"
    RECOMMENDED_NATARS = "recommended_natars"
    LOG = "actionsLog"
    EVENT_SUMMERY = "eventSummery"
    ERRORS = "errors"

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
        Collections.EVENT_SUMMERY,
        Collections.ERRORS,
    ]

class ArcgisSettings:
    SERVER_URL = 'https://menater-server.localdomain:6443/arcgis'
    LAYER_SERVER_URL = SERVER_URL + '/rest/services'
    PORTAL_URL = 'https://menater-server.localdomain/portal'
    USERNAME = 'admin'
    PASSWORD = 'Password1'
    BUILDINGS_LAYER = '/BeerSheva/MapServer/4'  # Buildings_Final
    NATARS_LAYER = '/BeerSheva/MapServer/1'  # Natarim_Final_New

