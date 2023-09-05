from enum import IntEnum

from battlebit_community_server_api.helper.StructHelper import write_uint8, read_uint8


class VehicleType(IntEnum):
    NONE = 0

    TANK = 1 << 1
    TRANSPORT = 1 << 2
    SEA_VEHICLE = 1 << 3
    APC = 1 << 4
    HELICOPTER = 1 << 5

    ALL = 255

    def as_bytes(self) -> bytes:
        return write_uint8(self.value)


def from_bytes(b: bytes) -> VehicleType:
    return VehicleType(read_uint8(b)[0])
