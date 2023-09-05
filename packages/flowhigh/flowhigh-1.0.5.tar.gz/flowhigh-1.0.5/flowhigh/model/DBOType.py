from enum import Enum


class DBOType(Enum):
    TABLE = 1
    COLUMN = 2
    DB = 3
    SCHEMA = 4
    VIEW = 5
    STAGE = 6

