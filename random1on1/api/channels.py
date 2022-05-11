"""
random1on1.api.channels

The channels classes are helpful wrappers around discord.TextChannel objects from the discord.py API. They provide helper functions to allow for the
random1on1 bot to perform common tasks (reading 1-on-1 matching history, sending out announcement messages etc). There is an abstract class 
AbstractRandom1on1Channel which encapsulates the general required information (e.g. a channel, the category for that channel, and the name of that 
channel). This abstract class has three implementations: 

    1. AnnouncementChannel: The announcment channel sends announcement messages to welcome the server to the random1on1 program and messages each 
                            week when the matches are made (as long as the bot is configured to announce matches publically)

    2. HistoryChannel: The history channel serves as a 'serverless database' that stores JSON messages that correspond to previous iterations of the
                        pairing algorithm. It provides a high level interface to both log these messsages and read-and-merge the collection of 
                        past matchings into a single pairing graph for the algorithm to use to avoid re-matching people who have been matched before. 

    3. LoggingChannel: The logging channel is a utility channel that is by default only visible to the administrators. The logging channel serves as
                        an easy way to surface matching runtime logs to the server administrators in a persistent and timely manner. The bot is 
                        designed to be run on ephemeral infrastructure, so these logs can become essential for debugging purposes.
"""
import json
import logging
import sys
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from functools import reduce

from discord import AllowedMentions
from discord import CategoryChannel
from discord import Role
from discord import TextChannel
from networkx import connected_components
from networkx import Graph
from networkx import union

from .pairings import Pairings
from .pairings import pairings_from_json

logger = logging.getLogger('discord')
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
logger.addHandler(stream)


async def fetch_or_create_channel_in_category(name: str,
                                              category: CategoryChannel):
    """
    Discord natively supports servers with multiple channels by the same name. This helper function either fetchs or creates a channel with a given 
    name in a category. If there are already multiple channels with the same name in the category, it throws an error (because the bot will not know
    which channel to use for sending and fetching future messages).
    
    Args:
        name (str) - the name of the channel to fetch or create 
        category (CategoryChannel) - the CategoryChannel in which to fetch or create the channel
    
    Return:
        A TextChannel object corresponding to the channel it found/created
        
    Raises: 
        ValueError - If the name is an empty string it will raise a value error because channels cannot have empty names
        RuntimeError - If multiple channels are found with the same name it will raise a RuntimeError
    """
    if len(name) == 0:
        raise ValueError("Cannot find or create channel with empty name")
    channels = [c for c in category.text_channels if c.name == name]
    if len(channels) == 0:
        logger.debug(
            "Found zero channels with name %s in category %s. Creating new channel now...",
            name, category.name)
        channel = await category.create_text_channel(name=name)
        logger.debug("Succesfully created channel with name %s in category %s",
                     name, category.name)
    elif len(channels) == 1:
        channel = channels[0]
        logger.debug(
            "Found existing channel with name %s in category with name %s",
            name, category.name)
    else:
        raise RuntimeError(
            f"Found multiple channels in category {category.name} with reserved channel name {name}"
        )
    return channel


class AbstractRandom1on1Channel(ABC):
    """ Abstract base class for channels that provides a generic constructor and a method signature for setting permissions on the underlying chanenl """

    def __init__(self, name: str, category: CategoryChannel,
                 channel: TextChannel):
        self.name = name
        self.category = category
        self.channel = channel

    @abstractmethod
    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        raise NotImplementedError(
            "AbstractRandom1on1Channel leaves the permissions implementation to its extensions"
        )


class AnnouncementChannel(AbstractRandom1on1Channel):

    @classmethod
    async def create(cls, name: str, category: CategoryChannel):
        """
        Class method that creates an announcment channel and sends the opening announcement. This method is used to avoid issues with async/await 
        method signatures from discord.py which do not interact easily with python 'magic methods' like __init__(...).

        Usage: 
            >>> name = 'Announcement Channel'
            >>> category = helper_to_get_proper_category(*args)
            >>> announcement_channel = AnnouncementChannel.create(name, category)

        Args: 
            name (str) - The name of the announcement channel
            category (CategoryChannel) - the category that you want to put the announcement channel in 

        Returns: 
            An AnnouncementChannel object which has already sent any necesary announcements. This object can later be used to log announcments of 
            pairings to the broader group of random 1 on 1 participants.
        """
        channel = await fetch_or_create_channel_in_category(name, category)
        announcement_channel = AnnouncementChannel(name, category, channel)
        _ = await announcement_channel.send_opening_announcement()
        return announcement_channel

    async def send_opening_announcement(self):
        """ Sends a generic introduction message to the announcement channel if the channel has not received any messages yet."""
        messages = await self.channel.history(limit=10).flatten()
        if len(messages) == 0:
            logger.debug(
                "Found zero previous messages in AnnouncementChannel %s. Sending introductory announcement.",
                self.name)
            _ = await self.channel.send("""
@everyone 

Hello Fellow Humans!

My name is the Random 1 on 1 bot! I will be running a program where you (if you choose to opt in) will be matched randomly every week with a new person from the discord server. The idea is to promote social interaction by getting everyone to meet new people from the server they might not have talked to before. I will send over an introduction to kick off a conversation, and then you and your partner for the week can take it from there. It's recommended that you spend at least 15 minutes for a chat (either over discord, or video conference or, if applicable, in person), but there's not hard and fast rules. The point of the program is just to have fun!

Have fun!

- Random 1 on 1 bot""")
        else:
            logger.debug(
                "Found previous announcement message in AnnouncementChannel %s. Opting to not send an introductory message",
                self.name)
            return True

    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        """ Sets appropriate read and write permissions for the announcments channel (everyone can read but only people participating in the program
        can send messages to the channel). """
        logger.debug(
            "Setting permissions for AnnouncementChannel: %s for default_role: %s and random1on1_role: %s",
            self.name, default_role.name, random1on1_role.name)
        logger.debug(
            "Setting permissions for roles. default_role is %s and is_role=%r",
            default_role.name, isinstance(default_role, Role))
        logger.debug(
            "Setting permissions for roles. random1on1_role is %s and is_role=%r",
            random1on1_role.name, isinstance(random1on1_role, Role))
        _ = await self.channel.set_permissions(target=default_role,
                                               read_messages=True,
                                               send_messages=False)
        _ = await self.channel.set_permissions(target=random1on1_role,
                                               read_messages=True,
                                               send_messages=True)

    async def announce_pairings(self, pairings: Pairings):
        """ Creates a simple announcement message from a collection of pairings and send it the announcement channel. """
        logger.debug(
            "Received for pairings week of %s, constructing announcement message",
            pairings.date_of_pairing.strftime('%Y-%m-%d'))
        announcement_message = f"""@everyone Announcing the pairings for Random 1 on 1s week of {datetime.now().strftime('%Y-%m-%d')}:\n---\n"""
        for component in connected_components(pairings.pairing_graph):
            announcement_message += ("/".join(
                [f"{participant.mention}"
                 for participant in component]) + "\n")
        _ = await self.channel.send(announcement_message,
                                    allowed_mentions=AllowedMentions.all())
        logger.debug(
            "Finished announcing pairings to the announcement channel")


class HistoryChannel(AbstractRandom1on1Channel):

    @classmethod
    async def create(cls, name: str, category: CategoryChannel):
        """
        Class method that creates a history channel. This method is used to avoid issues with async/await method signatures from discord.py which 
        do not interact easily with python 'magic methods' like __init__(...).

        Usage: 
            >>> name = 'History Channel'
            >>> category = helper_to_get_proper_category(*args)
            >>> announcement_channel = HistoryChannel.create(name, category)

        Args: 
            name (str) - The name of the history channel
            category (CategoryChannel) - the category that you want to put the announcement channel in 

        Returns: 
            An HistoryChannel object. This object can later be used to log the history of pairings for uwse by the matching algorithm on future 
            script runs. 
        """
        channel = await fetch_or_create_channel_in_category(name, category)
        history_channel = HistoryChannel(name, category, channel)
        return history_channel

    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        """ Sets appropriate read and write permissions for the history channel (only server admins can read -- messages are for the bots internal 
        use only)."""
        logger.debug(
            "Setting permissions for AnnouncementChannel: %s for default_role: %s and random1on1_role: %s",
            self.name, default_role.name, random1on1_role.name)
        logger.debug(
            "Setting permissions for roles. default_role is %s and is_role=%r",
            default_role.name, isinstance(default_role, Role))
        logger.debug(
            "Setting permissions for roles. random1on1_role is %s and is_role=%r",
            random1on1_role.name, isinstance(random1on1_role, Role))
        _ = await self.channel.set_permissions(target=default_role,
                                               read_messages=False)
        _ = await self.channel.set_permissions(target=random1on1_role,
                                               read_messages=False)

    async def write_pairings(self, pairings: Pairings):
        """ Sends the pairings to the channel. """
        _ = await self.channel.send(json.dumps(pairings.to_json()))

    async def read_historical_pairings(
            self,
            date_from: datetime = datetime(year=2022, month=1, day=1),
            date_to: datetime = datetime.now(),
    ) -> Pairings:
        """
        Collects previous pairings from all recent messages (recent as in within a certain time frame) and merges their matching-graphs into a single
        graph representing all the historical mathcings that have been computed by the algorithm in the past. This information is in turned used 
        by other classes (e.g. the algoirthms) to compute matchings and avoid re-matching people who have recently been paired together.

        Usage:
            >>> history_channel = get_history_channel()
            >>> async def create_new_pairings(history_channel, *args):
            >>>     previous_pairings_merged = history_channel.read_historical_pairings()
            >>>     # ... do stuff here to process the pairings and create the new matches. 

        Args: 
            date_from (datetime) - The datetime to start looking for messages from 
            date_to (datetime) - The datetime to serach for messages up until

        Returns: 
            A Pairings object with Pairings.pairing_graph representing the merged state of all previous graphs merged together.
        """
        # TODO: Remove all literals for translating datetime to from string and opt for some global constant
        logger.debug(
            "Searching for previous pairings logged in HistoryChannel: %s that took place between %s and %s.",
            self.name, date_from.strftime('%Y-%m-%d'),
            date_to.strftime('%Y-%m-%d'))
        all_official_pairings = []
        for message in await self.channel.history(after=date_from,
                                                  before=date_to).flatten():
            pairing = await pairings_from_json(message.content,
                                               self.channel.guild)
            logger.debug(
                "Found pairing object associated with date %s and dry_run=%r",
                pairing.date_of_pairing.strftime('%Y-%m-%d'), pairing.dry_run)
            if not pairing.dry_run:
                all_official_pairings.append(pairing)

        if len(all_official_pairings) > 0:
            logger.debug(
                "Found total of %f official (i.e. non-dry-run) pairings",
                len(all_official_pairings))
        else:
            logger.debug(
                "Found no previous pairings, indicating this is a first time pairings. Returning an empty pairings object"
            )
            return Pairings(
                pairing_graph=Graph(),
                date_of_pairing=datetime.now(),
                dry_run=False,
            )

        logger.debug("Unioning the pairing graphs together now")
        # TODO: Change this to a manual union method to add metadata for edges (e.g. the number of and dates of the meetings between two members).
        merged_pairing_graph = reduce(
            lambda G, H: union(G, H),
            [p.pairing_graph for p in all_official_pairings])

        merged_pairings = Pairings(
            pairing_graph=merged_pairing_graph,
            date_of_pairing=datetime.now(),
            dry_run=False,
        )

        logger.debug("Completed merging of pairings")
        return merged_pairings


class LoggingChannel(AbstractRandom1on1Channel):

    @classmethod
    async def create(cls, name: str, category: CategoryChannel):
        """ Creates a logging channel to be used with discord and python logging"""
        # TODO: This class requires proper implementation.
        channel = await fetch_or_create_channel_in_category(name, category)
        logging_channel = LoggingChannel(name, category, channel)
        return logging_channel

    async def set_permissions(self, default_role: Role, random1on1_role: Role):
        """ Sets appropriate read and write permissions for the logging channel (only server admins can read -- messages are debugging purposes)."""
        logger.debug(
            "Setting permissions for AnnouncementChannel: %s for default_role: %s and random1on1_role: %s",
            self.name, default_role.name, random1on1_role.name)
        logger.debug(
            "Setting permissions for roles. default_role is %s and is_role=%r",
            default_role.name, isinstance(default_role, Role))
        logger.debug(
            "Setting permissions for roles. random1on1_role is %s and is_role=%r",
            random1on1_role.name, isinstance(random1on1_role, Role))
        _ = await self.channel.set_permissions(target=default_role,
                                               read_messages=False)
        _ = await self.channel.set_permissions(target=random1on1_role,
                                               read_messages=False)
