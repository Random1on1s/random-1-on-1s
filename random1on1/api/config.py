import json

from preconditions import preconditions

DEFAULT_ROLE = "Random-1-on-1s"
DEFAULT_CATEGORY = "Random-1-on-1s"
DEFAULT_HISTORY_CHANNEL = "pairing-history"
DEFAULT_LOGGING_CHANNEL = "logs"
DEFAULT_ANNOUNCEMENT_CHANNEL = "random-1-on-1-announcements"


class Random1on1BotConfig(object):

    @preconditions(
        lambda guild_id: len(guild_id) > 0,
        lambda random1on1_role: len(random1on1_role) > 0,
        lambda channel_category: len(channel_category) > 0,
        lambda history_channel: len(history_channel) > 0,
        lambda logging_channel: len(logging_channel) > 0,
        lambda announcement_channel: len(announcement_channel) > 0,
    )
    def __init__(
        self,
        guild_id: str,
        random1on1_role: str = DEFAULT_ROLE,
        channel_category: str = DEFAULT_CATEGORY,
        history_channel: str = DEFAULT_HISTORY_CHANNEL,
        logging_channel: str = DEFAULT_LOGGING_CHANNEL,
        announcement_channel: str = DEFAULT_ANNOUNCEMENT_CHANNEL,
        dm_matches: bool = True,
        announce_matches: bool = True,
    ):
        self.guild_id = guild_id
        self.random1on1_role = random1on1_role
        self.channel_category = channel_category
        self.announcement_channel_name = announcement_channel
        self.history_channel_name = history_channel
        self.logging_channel_name = logging_channel
        self.dm_matches = dm_matches
        self.announce_matches = announce_matches

    @classmethod
    def from_json(cls, json_data: str):
        return cls(**json.loads(json_data))

    def to_json(self) -> str:
        return json.dumps(self,
                          default=lambda obj: obj.__dict__,
                          sort_keys=True,
                          indent=4)
