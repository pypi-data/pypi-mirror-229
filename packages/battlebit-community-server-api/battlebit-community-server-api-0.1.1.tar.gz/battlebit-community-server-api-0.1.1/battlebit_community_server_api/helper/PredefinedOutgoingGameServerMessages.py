from battlebit_community_server_api.model.OutgoingGameServerMessage import OutgoingGameServerMessage
from battlebit_community_server_api.model.OpCodes import OpCodes
from battlebit_community_server_api.model.PlayerModification import PlayerModification
from battlebit_community_server_api.model.SteamId import SteamId
from battlebit_community_server_api.model.Vector3 import Vector3
from battlebit_community_server_api.model.VoxelBlockData import VoxelBlockData


class SetPlayerModification(OutgoingGameServerMessage):
    def __init__(self, steam_id: SteamId, player_modifications: PlayerModification):
        super().__init__(OpCodes.SET_PLAYER_MODIFICATIONS)
        self.add_bytes(steam_id.to_bytes())
        self.add_bytes(player_modifications.as_bytes())


class PlaceVoxelBlock(OutgoingGameServerMessage):
    def __init__(self, voxel_position: Vector3, voxel_data: VoxelBlockData):
        super().__init__(OpCodes.PLACE_VOXEL_BLOCK)
        self.add_bytes(voxel_position.as_bytes())
        self.add_bytes(voxel_data.as_bytes())


class DestroyVoxelBlock(OutgoingGameServerMessage):
    def __init__(self, voxel_position: Vector3):
        super().__init__(OpCodes.REMOVE_VOXEL_BLOCK)
        self.add_bytes(voxel_position.as_bytes())
