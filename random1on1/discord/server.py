from random1on1.api.channels import AnnouncementChannel, HistoryChannel, LoggingChannel
from random1on1.api.participant import Partitipant


class Random1on1Server:

    def __init__(self, token: str):
        # TODO: Figure out what you need to uniquely identify a server
        self.token = token
        raise NotImplementedError()

    def get_participants(self, random1on1_role: str) -> list[Participant]:
        raise NotImplementedError()

    def setup_channels(
        self,
        announce_channel: AnnouncementChannel = None,
        history_channel: HistoryChannel = None,
        logging_channel: LoggingChannel = None,
    ):
        raise NotImplementedError()
