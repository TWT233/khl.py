"""common hax"""


def unpack_id(obj):
    """extract obj's id if not basic data type"""
    return obj if isinstance(obj, (str, int)) else obj.id


def unpack_value(enum):
    """extract enum's value if not basic data type"""
    return enum if isinstance(enum, (str, int)) else enum.value
