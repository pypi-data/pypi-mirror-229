from enum import Enum


class Task(str, Enum):
    RUN_SERVICE = "RUN_SERVICE"
    LIST_SERVICES = "LIST_SERVICES"
    GET_SERVICE_DETAILS = "GET_SERVICE_DETAILS"


class ServerTask(str, Enum):
    UPDATE_AGENT_STATUS = "UPDATE_AGENT_STATUS"
    UPDATE_SERVICE_STATUS = "UPDATE_SERVICE_STATUS"
    UPDATE_SERVICE_OUTPUTS = "UPDATE_SERVICE_OUTPUTS"


class InputType(str, Enum):
    BUTTON = "button"
    CHECKBOX = "checkbox"
    COLOR = "color"
    DATE = "date"
    DATETIME_LOCAL = "datetime-local"
    EMAIL = "email"
    FILE = "file"
    HIDDEN = "hidden"
    IMAGE = "image"
    MONTH = "month"
    NUMBER = "number"
    PASSWORD = "password"
    RADIO = "radio"
    RANGE = "range"
    RESET = "reset"
    SEARCH = "search"
    SUBMIT = "submit"
    TEL = "tel"
    TEXT = "text"
    TIME = "time"
    URL = "url"
    WEEK = "week"
