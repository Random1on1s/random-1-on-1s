import json
from dataclasses import dataclass
from typing import Union

DEFAULT_ANNOUNCEMENT_CHANNEL = "random-1-on-1-announcements"
DEFAULT_CATEGORY = "Random 1-on-1s"
DEFAULT_HISTORY_CHANNEL = "random-1-on-1-bot-history"
DEFAULT_LOGGING_CHANNEL = "random-1-on-1-bot-logs"
DEFAULT_ROLE = "Random 1-on-1s"
DEFAULT_ANNOUNCE_MATCHES = True
DEFAULT_DM_MATCHES = True


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

    def __post_init__(self):
        validate_announcement_prefs(**{'guild_id': self.guild_id, 'dm_matches': self.dm_matches, 'announce_matches': self.announce_matches})

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
    if not "guild_id" in dictionary:
        raise ValueError("Every configuration needs to specify guild_id")
    if "dm_matches" in dictionary and "announce_matches" in dictionary:
        if not (isinstance(dictionary["announce_matches"], bool)
                or isinstance(dictionary["dm_matches"], bool)):
            raise ValueError(
                "announce_matches and dm_matches must be type 'bool'")
        if dictionary["announce_matches"] == False and dictionary["dm_matches"] == False:
            raise ValueError("announce_matches and dm_matches cannot both be false") 


def config_from_dict(dictionary) -> Random1on1BotConfig:
    validate_announcement_prefs(**dictionary)
    return Random1on1BotConfig(
        guild_id=dictionary["guild_id"],
        random1on1_role=dictionary.get("random1on1_role", DEFAULT_ROLE),
        channel_category=dictionary.get("channel_category", DEFAULT_CATEGORY),
        announcement_channel=dictionary.get("announcement_channel", DEFAULT_ANNOUNCEMENT_CHANNEL),
        history_channel=dictionary.get("history_channel", DEFAULT_HISTORY_CHANNEL),
        logging_channel=dictionary.get("logging_channel", DEFAULT_LOGGING_CHANNEL),
        announce_matches=dictionary.get("announce_matches", DEFAULT_ANNOUNCE_MATCHES),
        dm_matches=dictionary.get("dm_matches", DEFAULT_DM_MATCHES),
    )
