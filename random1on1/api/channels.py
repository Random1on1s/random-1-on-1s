import json
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from functools import reduce

from discord import CategoryChannel
from discord import Role
from discord import TextChannel
from networkx import connected_components
from networkx import union
from preconditions import preconditions

from .pairings import Pairings


class AbstractRandom1on1Channel(ABC):

    @preconditions(lambda name: len(name) > 0)
    async def __init__(self, name: str, category: CategoryChannel):
        self.name = name
        channels = [c for c in category.text_channels if c.name == self.name]
        if len(channels) == 0:
            channel = await category.create_text_channel(name=self.name)
        elif len(channels) == 1:
            channel = channels[0]
        else:
            raise RuntimeError(
                f"Found multiple channels in category {category.name} with reserved channel name {self.name}"
            )

        self.channel = channel

    @abstractmethod
    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        yield


class AnnouncementChannel(AbstractRandom1on1Channel):

    def __init__(self, name: str, category: CategoryChannel):
        super().__init__(name, category)
        _ = self.send_opening_announcement()

    async def send_opening_announcement(self):
        messages = await self.channel.history(limit=1).flatten()
        if len(messages) == 0:
            self.channel.send("""
                Hello Fellow Humans!

                My name is the Random 1 on 1 bot! I will be running a program where you (if you choose to opt in) will be matched randomly every week
                with a new person from the discord server. The idea is to promote social interaction by getting everyone to meet new people from the
                server they might not have talked to before. I will send over an introduction to kick off a conversation, and then you and your 
                partner for the week can take it from there. It's recommended that you spend at least 15 minutes for a chat (either over discord, 
                or video conference or, if applicable, in person), but there's not hard and fast rules. The point of the program is just to have fun!

                Have fun!

                - Random 1 on 1 bot
            """)

    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        _ = self.channel.set_permissions(default_role,
                                         read_messages=True,
                                         write_messages=False)
        _ = self.channel.set_permissions(random1on1_role,
                                         read_messages=True,
                                         write_messages=True)

    async def announce_pairings(self, pairings: Pairings):
        announcement_message = f"""
        Announcing the pairings for Random 1 on 1s week of {datetime.now().strftime('%Y-%m-%d')}:
        ---
        """
        for component in connected_components(pairings.pairing_graph):
            announcement_message += "/".join(
                [participant.name for participant in component]) + "\n"
        _ = self.channel.send(announcement_message)


class HistoryChannel(AbstractRandom1on1Channel):

    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        _ = self.channel.set_permissions(default_role, read_messages=False)
        _ = self.channel.set_permissions(random1on1_role, read_messages=False)

    async def write_pairings(self, pairings: Pairings, dry_run: bool):
        pairings_message = {"dry_run": dry_run, "pairings": pairings.to_json()}
        _ = self.channel.send(json.dumps(pairings_message))

    async def read_historical_pairings(
        self,
        date_to: datetime = datetime.now(),
        date_from: datetime = datetime(year=1970, month=1, day=1),
    ) -> Pairings:

        all_pairings = []
        for message in await self.channel.history(after=date_from,
                                                  before=date_to).flatten():
            serialized_message = json.load(message.content)
            if "dry_run" in serialized_message.keys():
                if not serialized_message["dry_run"]:
                    pairings = Pairings.from_json(
                        serialized_message["pairings"])
                    all_pairings.append(pairings)

        merged_pairing_graph = reduce(lambda G, H: union(G, H),
                                      [p.pairing_graph for p in all_pairings])

        merged_pairings = Pairings(pairing_graph=merged_pairing_graph,
                                   date_of_pairing=datetime.now(),
                                   dry_run=False)
        return merged_pairings


class LoggingChannel(AbstractRandom1on1Channel):

    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        _ = self.channel.set_permissions(default_role, read_messages=False)
        _ = self.channel.set_permissions(random1on1_role, read_messages=False)
