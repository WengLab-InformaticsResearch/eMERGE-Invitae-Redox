from enum import Enum


class YesNo(Enum):
    NO = '0'
    YES  = '1'

class Complete(Enum):
    INCOMPLETE = '0'
    UNVERIFIED = '1'
    COMPLETE = '2'