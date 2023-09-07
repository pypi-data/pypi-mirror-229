# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from acme_client.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    PAGINATION = "/pagination"
    PET = "/pet"
    PET_FIND_BY_STATUS = "/pet/findByStatus"
    PET_FIND_BY_TAGS = "/pet/findByTags"
    PET_PET_ID = "/pet/{petId}"
    PET_PET_ID_UPLOAD_IMAGE = "/pet/{petId}/uploadImage"
    STORE_INVENTORY = "/store/inventory"
    STORE_ORDER = "/store/order"
    STORE_ORDER_ORDER_ID = "/store/order/{orderId}"
    USER = "/user"
    USER_CREATE_WITH_ARRAY = "/user/createWithArray"
    USER_CREATE_WITH_LIST = "/user/createWithList"
    USER_LOGIN = "/user/login"
    USER_LOGOUT = "/user/logout"
    USER_USERNAME = "/user/{username}"
