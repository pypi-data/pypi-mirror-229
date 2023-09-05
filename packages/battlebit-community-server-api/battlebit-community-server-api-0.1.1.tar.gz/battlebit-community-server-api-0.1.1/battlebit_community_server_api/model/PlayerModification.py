from dataclasses import dataclass

from battlebit_community_server_api.model.SpawningRule import SpawningRule
from battlebit_community_server_api.model.VehicleType import VehicleType
from battlebit_community_server_api.helper.StructHelper import *


@dataclass
class PlayerModification:
    running_speed_multiplier: float = 1.0
    receive_damage_multiplier: float = 1.0
    give_damage_multiplier: float = 1.0
    jump_height_multiplier: float = 1.0
    fall_damage_multiplier: float = 1.0
    reload_speed_multiplier: float = 1.0
    can_use_night_vision: bool = True
    down_time_give_up_time: float = 60.0
    can_air_strafe: bool = True
    can_deploy: bool = True
    can_spectate: bool = True
    is_muted_in_text_chat: bool = False
    is_muted_in_voice_chat: bool = False
    respawn_time: float = 10.0
    can_suicide: bool = True
    min_damage_to_start_bleeding: float = 10.0
    min_hp_to_start_bleeding: float = 40.0
    hp_gain_per_bandage: float = 40.0
    has_stamina_enabled: bool = False
    has_hit_markers_enabled: bool = True
    can_see_friendlies_on_hud: bool = True
    capture_flag_speed_multiplier: float = 1.0
    can_see_point_log_on_hud: bool = True
    can_see_kill_feed: bool = False
    is_exposed_on_map: bool = False
    spawning_rule: SpawningRule = SpawningRule.ALL
    allowed_vehicle_types: VehicleType = VehicleType.ALL
    is_frozen: bool = False
    hit_points_upon_revive: float = 35.0
    is_hidden_on_map: bool = False

    def as_bytes(self) -> bytes:
        out = write_float32(self.running_speed_multiplier) if self.running_speed_multiplier > 0 else write_float32(0.01)
        out += write_float32(self.receive_damage_multiplier)
        out += write_float32(self.give_damage_multiplier)
        out += write_float32(self.jump_height_multiplier)
        out += write_float32(self.fall_damage_multiplier)
        out += write_float32(self.reload_speed_multiplier)
        out += write_bool(self.can_use_night_vision)
        out += write_float32(self.down_time_give_up_time)
        out += write_bool(self.can_air_strafe)
        out += write_bool(self.can_deploy)
        out += write_bool(self.can_spectate)
        out += write_bool(self.is_muted_in_text_chat)
        out += write_bool(self.is_muted_in_voice_chat)
        out += write_float32(self.respawn_time)
        out += write_bool(self.can_suicide)
        out += write_float32(self.min_damage_to_start_bleeding)
        out += write_float32(self.min_hp_to_start_bleeding)
        out += write_float32(self.hp_gain_per_bandage)
        out += write_bool(self.has_stamina_enabled)
        out += write_bool(self.has_hit_markers_enabled)
        out += write_bool(self.can_see_friendlies_on_hud)
        out += write_float32(self.capture_flag_speed_multiplier)
        out += write_bool(self.can_see_point_log_on_hud)
        out += write_bool(self.can_see_kill_feed)
        out += write_bool(self.is_exposed_on_map)
        out += self.spawning_rule.as_bytes()
        out += self.allowed_vehicle_types.as_bytes()
        out += write_bool(self.is_frozen)
        out += write_float32(self.hit_points_upon_revive)
        out += write_bool(self.is_hidden_on_map)
        return out


def from_bytes(d: bytes) -> PlayerModification:

    r, d = read_float32(d)
    if r <= 0:
        running_speed_multiplier = 0.01
    else:
        running_speed_multiplier = r
    receive_damage_multiplier, d = read_float32(d)
    give_damage_multiplier, d = read_float32(d)
    jump_height_multiplier, d = read_float32(d)
    fall_damage_multiplier, d = read_float32(d)
    reload_speed_multiplier, d = read_float32(d)
    can_use_night_vision, d = read_bool(d)
    down_time_give_up_time, d = read_float32(d)
    can_air_strafe, d = read_bool(d)
    can_deploy, d = read_bool(d)
    can_spectate, d = read_bool(d)
    is_muted_in_text_chat, d = read_bool(d)
    is_muted_in_voice_chat, d = read_bool(d)
    respawn_time, d = read_float32(d)
    can_suicide, d = read_bool(d)
    min_damage_to_start_bleeding, d = read_float32(d)
    min_hp_to_start_bleeding, d = read_float32(d)
    hp_gain_per_bandage, d = read_float32(d)
    has_stamina_enabled, d = read_bool(d)
    has_hit_markers_enabled, d = read_bool(d)
    can_see_friendlies_on_hud, d = read_bool(d)
    capture_flag_speed_multiplier, d = read_float32(d)
    can_see_point_log_on_hud, d = read_bool(d)
    can_see_kill_feed, d = read_bool(d)
    is_exposed_on_map, d = read_bool(d)
    spawning_rule, d = read_uint64(d)
    spawning_rule = SpawningRule(spawning_rule)
    allowed_vehicle_types, d = read_uint8(d)
    allowed_vehicle_types = VehicleType(allowed_vehicle_types)
    is_frozen, d = read_bool(d)
    hit_points_upon_revive, d = read_float32(d)
    is_hidden_on_map, _ = read_bool(d)
    return PlayerModification(running_speed_multiplier, receive_damage_multiplier, give_damage_multiplier,
                              jump_height_multiplier, fall_damage_multiplier, reload_speed_multiplier,
                              can_use_night_vision, down_time_give_up_time, can_air_strafe, can_deploy, can_spectate,
                              is_muted_in_text_chat, is_muted_in_voice_chat, respawn_time, can_suicide,
                              min_damage_to_start_bleeding, min_hp_to_start_bleeding, hp_gain_per_bandage,
                              has_stamina_enabled, has_hit_markers_enabled, can_see_friendlies_on_hud,
                              capture_flag_speed_multiplier, can_see_point_log_on_hud, can_see_kill_feed,
                              is_exposed_on_map, spawning_rule, allowed_vehicle_types, is_frozen,
                              hit_points_upon_revive, is_hidden_on_map)
