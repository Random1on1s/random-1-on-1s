import json
from dataclasses import dataclass
from typing import Union

DEFAULT_ANNOUNCEMENT_CHANNEL = "random-1-on-1-announcements"
DEFAULT_CATEGORY = "Random 1-on-1s"
DEFAULT_HISTORY_CHANNEL = "random-1-on-1-bot-history"
DEFAULT_LOGGING_CHANNEL = "random-1-on-1-bot-logs"
DEFAULT_ROLE = "Random 1-on-1s"


@dataclass(frozen=True)
class Random1on1BotConfig(object):

    guild_id: int
    random1on1_role: str = DEFAULT_ROLE
    channel_category: str = DEFAULT_CATEGORY
    announcement_channel: str = DEFAULT_ANNOUNCEMENT_CHANNEL
    history_channel: str = DEFAULT_HISTORY_CHANNEL
    logging_channel: str = DEFAULT_LOGGING_CHANNEL
    announce_matches: bool = True
    dm_matches: bool = True

    def to_json(self) -> str:
        return json.dumps(self,
                          default=lambda obj: obj.__dict__,
                          sort_keys=True,
                          indent=4)


def config_from_json(json_data: Union[str, dict]) -> Random1on1BotConfig:
    if isinstance(json_data, str):
        return config_from_dict(dictionary=json.loads(json_data))
    else:
        return config_from_dict(dictionary=json_data)


def validate_announcement_prefs(**dictionary):
    if "dm_matches" in dictionary and "announce_matches" in dictionary:
        if not (isinstance(dictionary["announce_matches"], bool)
                and isinstance(dictionary["dm_matches"], bool)):
            raise TypeError(
                "announce_matches and dm_matches must be type 'bool'")
        return dictionary["announce_matches"] or dictionary["dm_matches"]


def config_from_dict(**dictionary) -> Random1on1BotConfig:
    validate_announcement_prefs(**dictionary)
    return Random1on1BotConfig(
        guild_id=dictionary["guild_id"],
        random1on1_role=dictionary["random1on1_role"],
        channel_category=dictionary["channel_category"],
        announcement_channel=dictionary["announcement_channel"],
        history_channel=dictionary["history_channel"],
        logging_channel=dictionary["logging_channel"],
        announce_matches=dictionary["announce_matches"],
        dm_matches=dictionary["dm_matches"],
    )
