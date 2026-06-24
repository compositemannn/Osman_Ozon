from enum import Enum


class HandlerResponse(str, Enum):
    ORDER_IS_NOT_EXIST_IN_DB = "ORDER_IS_NOT_EXIST_IN_DB"
    OK = "OK"
