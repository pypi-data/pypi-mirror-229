from enum import Enum


# TODO: We should order them by alphabet of the Entity

class ActionName(Enum):
    
    ADD_LOG = "add"
    ANALYZE_FACIAL_IMAGE = "analyzeFacialImage"
    CREATE_EVENT = "createEvent"
    CREATE_USER = "createUser"
    DELETE_EVENT_BY_ID = "deleteEventById"
    GENDER_DETECTION = "process"
    GET_ALL_GROUPS = "getAllGroups"
    GET_EVENT_BY_ID = "getEventById"
    GET_GROUP_BY_ID = "getGroupById"
    GET_GROUP_BY_NAME = "getGroupByName"
    GRAPHQL = "graphql"
    LOGIN = "login"
    TIMELINE = "timeline"
    UPDATE_EVENT_BY_ID = "updateEventById"
    UPDATE_USER = "updateUser"
    VALIDATE_JWT = 'validateJwt'
    