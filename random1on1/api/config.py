import json


class Random1on1BotConfig(object):
    # TODO: Add configuration values and precondition checks here

    def __init__(
        self,
        random1on1_role: str,
        history_channel: str,
        logging_channel: str,
        announcement_channel: str,
        dm_matches: bool,
        announce_matches: bool,
    ):
        self.random1on1_role = random1on1_role
        self.history_channel = history_channel
        self.logging_channel = logging_channel
        self.announcement_channel = announcement_channel
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
