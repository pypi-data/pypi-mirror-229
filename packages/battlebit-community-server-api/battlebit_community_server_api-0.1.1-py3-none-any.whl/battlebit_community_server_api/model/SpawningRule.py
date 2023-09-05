from enum import IntEnum

from battlebit_community_server_api.helper.StructHelper import write_uint64, read_uint64


class SpawningRule(IntEnum):
    NONE = 0

    FLAGS = 1 << 0
    SQUAD_MATES = 1 << 1
    SQUAD_CAPTAIN = 1 << 2

    TANKS = 1 << 3
    TRANSPORTS = 1 << 4
    BOATS = 1 << 5
    HELICOPTERS = 1 << 6
    APCS = 1 << 7

    RALLY_POINTS = 1 << 8

    ALL = 18446744073709551615  # Why Oki?

    def as_bytes(self) -> bytes:
        return write_uint64(self.value)


def from_bytes(b: bytes) -> SpawningRule:
    return SpawningRule(read_uint64(b)[0])
