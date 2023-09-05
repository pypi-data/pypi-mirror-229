import logging

from battlebit_community_server_api.ApiServer import ApiServer, build_api_server
from battlebit_community_server_api.model.OpCodes import OpCodes
from battlebit_community_server_api.service.TcpParsingService import TcpParsingService
from battlebit_community_server_api.model.SteamId import SteamId
from battlebit_community_server_api.helper.PredefinedOutgoingGameServerMessages import SetPlayerModification
from battlebit_community_server_api.model.PlayerModification import PlayerModification
from battlebit_community_server_api.handler.DefaultHandlers import DefaultHandlers

my_api_server: ApiServer = build_api_server("0.0.0.0", 30000, None)
MY_OWN_STEAM_ID = SteamId(76561198082868306)
MY_CHEATER_MODIFICATION = PlayerModification(
    give_damage_multiplier=3.5,
    receive_damage_multiplier=0.3,
    jump_height_multiplier=2.2,
    is_hidden_on_map=True
)


async def cheating_admin_handler(data: bytes) -> bytes:
    """
    This function:

    1. parses the data received by the "On Player Joining" event.
    2. Checks if the SteamID is identical to a specific player
    3. Queues a player modification
    4. Invokes the default handler and returns the result
    """
    steam_id, player_stats = TcpParsingService.parse_on_player_joining(data)
    if MY_OWN_STEAM_ID == steam_id:
        await my_api_server.add_outgoing_game_server_message_to_queue(
            SetPlayerModification(MY_OWN_STEAM_ID, MY_CHEATER_MODIFICATION)
        )
    return await DefaultHandlers.on_player_joining_handler(data)


logging.basicConfig(level=logging.DEBUG)  # Optional: If you want to have an in-depth view into what's going on.
my_api_server.register_handler(OpCodes.ON_PLAYER_JOINING, cheating_admin_handler)

my_api_server.start()
