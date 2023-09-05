from dataclasses import dataclass
from enum import IntEnum

from helper.StructHelper import write_uint8, read_uint8


class VoxelTexture(IntEnum):
    DEFAULT = 0
    NEON_ORANGE = 1

    def as_bytes(self) -> bytes:
        return write_uint8(self.value)


def texture_from_bytes(d: bytes) -> VoxelTexture:
    return VoxelTexture(read_uint8(d)[0])


@dataclass
class VoxelBlockData:
    texture: VoxelTexture

    def as_bytes(self) -> bytes:
        return self.texture.as_bytes()


def block_data_from_bytes(d: bytes) -> VoxelBlockData:
    return VoxelBlockData(texture_from_bytes(d))
