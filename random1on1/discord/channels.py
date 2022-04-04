from random1on1.api.channel import ReadWriteChannel
from random1on1.api.channel import WriteOnlyChannel
from random1on1.api.channel import WriteOnlyDirectMessages
from random1on1.api.pairings import Pairings
from random1on1.api.participant import Participant


class HistoryChannel(ReadWriteChannel):

    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        raise NotImplementedError()

    async def write_pairings(self, pairings: Pairings, dry_run: bool):
        raise NotImplementedError()

    async def read_historical_pairings(self) -> Pairings:
        raise NotImplementedError()


class LoggingChannel(WriteOnlyChannel):

    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        raise NotImplementedError()


class AnnouncementChannel(WriteOnlyChannel):

    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        raise NotImplementedError()


class PairingsDmChannel(WriteOnlyDirectMessages):

    def __init__(
        self,
        channel_name: str,
        participants: list[Participant],
    ):
        super().__init__(channel_name, participants)
        raise NotImplementedError()
