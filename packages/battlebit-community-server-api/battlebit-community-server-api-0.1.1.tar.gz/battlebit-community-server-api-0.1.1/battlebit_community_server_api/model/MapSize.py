from enum import IntEnum


class MapSize(IntEnum):
    NONE = 0
    TINY = 8     # 8vs8
    SMALL = 16   # 16vs16
    MEDIUM = 32  # 32vs32
    BIG = 64     # 64vs64
    ULTRA = 90   # 127vs127
