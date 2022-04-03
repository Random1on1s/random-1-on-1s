from abc import ABC, abstractmethod
from discord.channel import TextChannel, GroupChannel
from random1on1.api.participant import Participant


class ReadWriteChannel(ABC, TextChannel):
    @abstractmethod
    def __init__(self, channel_name: str):
        # TODO: Add precondition checks here
        self.channel_name = channel_name


class WriteOnlyChannel(ABC, TextChannel):
    @abstractmethod
    def __init__(self, channel_name: str):
        # TODO: Add preconditions here
        self.channel_name = channel_name


class WriteOnlyDirectMessages(ABC, GroupChannel):
    @abstractmethod
    def __init__(
        self,
        channel_name: str,
        participants: list[Participant],
    ):
        # TODO: Add proconditions here
        self.channel_name = channel_name
        self.participants = participants
