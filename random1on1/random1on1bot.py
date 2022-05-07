"""
The Random1on1Bot class is the code that does all the heavy lifting in connecting to discord, setting up channels and roles, tweaking permissions, 
reading in previous match history, running a 1-on-1 matching algorithm, and then sending out all the matches to the rest of the discord server. The 
Random1on1Bot class itself is a wrapper on the discord.Client object and all the work is done through the on_ready() method and the subsequent helper
methods that it calls. 
"""
import logging
import sys
from typing import List

from discord import AllowedMentions
from discord import CategoryChannel
from discord import Client
from discord import Member
from networkx import connected_components

from random1on1.api.channels import AnnouncementChannel
from random1on1.api.channels import HistoryChannel
from random1on1.api.channels import LoggingChannel
from random1on1.api.config import config_from_json
from random1on1.api.config import Random1on1BotConfig
from random1on1.matching.uniform import UniformMatchingAlgorithm

logger = logging.getLogger("discord")
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
logger.addHandler(stream)


def read_config(location):
    # TODO: Move this method to Random1on1BotConfig
    with open(location, "r") as config_file:
        config = config_from_json(config_file.read())
    return config


class Random1on1Bot(Client):

    def __init__(self,
                 config: Random1on1BotConfig,
                 dry_run: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.dry_run = dry_run
        logger.setLevel(level=logging.DEBUG)

        # TODO: Add logging handler here for writing logs to #random1on1-bot-logs channel
        # TODO: Add logging to all the elements we want

    async def on_ready(self):
        """
        on_ready() does the heavy lifting of calling other methods within the Random1on1Bot via a number of different helper methods. It works by 
        first checking the guild for the proper setup (channels, category, and role all matching those specified by name in the Random1on1BotConfig 
        file on disk) and then calling the run_matching_program() method which uses these setup access points for the server to actually pull the
        proper information and send the messages to their appropriate channels. 

        Usage (note to use this method, you do not have to call it directly): 
            >>> from random1on1.random1on1bot import Random1on1Bot
            >>> from random1on1.api.config import Random1on1BotConfig
            >>> config = Random1on1BotConfig(guild_id=1) # put your guild id here
            >>> token = '<discord access token goes here>'
            >>> bot = Random1on1Bot(config=config) 
            >>> bot.run(token) # This implicitly calls the on_ready() method when it connects to discord
        """

        logger.debug("Setting up random1on1bot with config values %r",
                     self.config)
        guild = self.get_guild(self.config.guild_id)
        if not guild:
            raise RuntimeError(
                f"Specified guild id: {self.config.guild_id} could not be found."
            )
        self.guild = guild

        self.category = await self.get_random1on1_category()
        self.random1on1_role = await self.get_random1on1_role()
        self.default_role = await self.get_default_role()
        self.announcement_channel = await self.get_announcement_channel()
        self.history_channel = await self.get_history_channel()
        self.logging_channel = await self.get_logging_channel()
        logger.debug("Successfully setup random1on1bot")

        logger.debug("Running random1on1bot's pairing method")
        _ = await self.run_matching_program()
        logger.debug("Completed the matching program")

        _ = await self.close()

    async def get_random1on1_category(self) -> CategoryChannel:
        """
        Discord natively supports servers with multiple categories by the same name. This helper function either fetchs or creates a category with a 
        given name. If there are already multiple categories with the same name, it throws an error (because the bot will not know which category 
        to use for its protected channels). 
       
        Return:
            A CategoryChannel object corresponding to the category it found/created
            
        Raises: 
            RuntimeError - If multiple categories are found with the same name it will raise a RuntimeError
        """
        categories = []
        for category in self.guild.categories:
            if category.name == self.config.channel_category:
                categories.append(category)

        if len(categories) == 0:
            logger.debug(
                "Found zero categories with name %s. Creating one now",
                self.config.channel_category)
            category = await self.guild.create_category_channel(
                name=self.config.channel_category)
            logger.debug("Successfully created category %s",
                         self.config.channel_category)
        elif len(categories) == 1:
            logger.debug("Found category with name %s",
                         self.config.channel_category)
            category = categories[0]
        else:
            raise RuntimeError(
                f"Found multiple categories of name {self.config.channel_category}"
            )

        return category

    async def get_default_role(self):
        # TODO: Change default viewer role e.g. so we can restrict that random1on1s category to people who have some sort of membership role
        return self.guild.default_role

    async def get_random1on1_role(self):
        """
        Discord natively supports servers with multiple roles by the same name. This helper function either fetchs or creates a role with a given 
        name. If there are already multiple roles with the same name, it throws an error (because the bot will not know which members it should 
        include in the pairings for Random 1 on 1s).
       
        Return:
            A Role object corresponding to the role it found/created
            
        Raises: 
            RuntimeError - If multiple roles are found with the same name it will raise a RuntimeError
        """
        random1on1_roles = [
            r for r in self.guild.roles
            if r.name == self.config.random1on1_role
        ]
        if len(random1on1_roles) == 0:
            logger.debug(
                "Found zero roles with name %s. Creating the role now.",
                self.config.random1on1_role)
            random1on1_role = await self.guild.create_role(
                name=self.config.random1on1_role,
                mentionable=True,
                reason=
                f"Role: {self.config.random1on1_role} required for Random 1-on-1s did not exist, so I created it!",
            )
            logger.debug("Successfully created role %s",
                         self.config.random1on1_role)
        elif len(random1on1_roles) == 1:
            logger.debug("Found role with name %s",
                         self.config.random1on1_role)
            random1on1_role = random1on1_roles[0]
        else:
            raise RuntimeError(
                f"Found multiple roles of name {self.config.random1on1_role}")

        return random1on1_role

    async def get_announcement_channel(self) -> AnnouncementChannel:
        """ Creates and sets permissions on the announcement channel based on the default_role and random1on1_role found by the client """
        announcement_channel = await AnnouncementChannel.create(
            name=self.config.announcement_channel, category=self.category)
        _ = await announcement_channel.set_permissions(
            default_role=self.default_role,
            random1on1_role=self.random1on1_role)
        return announcement_channel

    async def get_history_channel(self) -> HistoryChannel:
        """ Creates and sets permissions on the history channel based on the default_role and random1on1_role found by the client """
        history_channel = await HistoryChannel.create(
            name=self.config.history_channel, category=self.category)
        _ = await history_channel.set_permissions(
            default_role=self.default_role,
            random1on1_role=self.random1on1_role)
        return history_channel

    async def get_logging_channel(self) -> LoggingChannel:
        """ Creates and sets permissions on the logging channel based on the default_role and random1on1_role found by the client """
        logging_channel = await LoggingChannel.create(
            name=self.config.logging_channel, category=self.category)
        _ = await logging_channel.set_permissions(
            default_role=self.default_role,
            random1on1_role=self.random1on1_role)
        return logging_channel

    async def get_participants(self) -> List[Member]:
        """ Gets a list of all members of the random1on1_role """
        role = await self.get_random1on1_role()
        return role.members

    async def run_matching_program(self):
        """ 
        run_matching_program method runs the matching program by fetching required information from channels setup for the random1on1 bot and then 
        creating an instance of the matching algorithm and running it based on the historical data. After receiving the pairings, if the configuration
        is setup properly it announces the pairings and/or creates group direct message channels with the pairing members. 

        Args: 
            dry_run (bool) - A boolean parameter used to flag certain instances of hte matching program as a test run (i.e. not to be factored in to 
                             future matching criteria or announced to the broader public).
        """

        logger.debug(
            "Fetching information to run the matching algorithm for random1on1 pairings"
        )
        participants = await self.get_participants()

        if len(participants) == 0:
            logger.debug(
                "No one is participating this week, so will stop the program early"
            )
            return

        previous_pairings_merged = await self.history_channel.read_historical_pairings(
        )
        logger.debug(
            "Finished fetching information to run the matching algorithm for random1on1 pairings"
        )

        # TODO: Make algorithms modular
        #       Currently we don't have a way to encode algorithms in a modular fashion. We should set up a way to encode algorithms in a modular
        #       fashion so that someone can specify an algorithm in the config, e.g. if they want the uniform sampling algorithm, their config
        #       should look like
        #       ```json
        #           {
        #               "algorithm": "UniformMatchingAlgorithm",
        #               // other config stuff goes here.
        #           }
        #       ```

        matching_algorithm = UniformMatchingAlgorithm(
            participants=participants,
            previous_pairings_merged=previous_pairings_merged)
        logger.debug(
            "Constructed instance of random1on1 algorithm. Starting to run matching program."
        )
        pairings = matching_algorithm.generate_pairs(dry_run=self.dry_run)
        logger.debug(
            "Succesfully matched participants for random1on1s on date_of_pairing: %s with dry_run: %r",
            pairings.date_of_pairing.strftime('%Y-%m-%d'), pairings.dry_run)
        _ = await self.history_channel.write_pairings(pairings)

        if not self.dry_run:
            if self.config.announce_matches:
                logger.debug("Announcing pairings in the announcement channel")
                _ = await self.announcement_channel.announce_pairings(pairings)
            if self.config.dm_matches:
                logger.debug(
                    "Iterating through pairings to create direct message groups for matched participants"
                )
                bot_user = self.user
                if not bot_user:
                    raise RuntimeError(
                        "Unable to communicate with bot user required for creating pairing groups"
                    )

                async def send_intro_dm(pairing_group):
                    logger.debug(
                        "Creating pairing group chat for %f many people based on pairing group %r",
                        len(pairing_group),
                        [member.name for member in pairing_group])
                    all_members = list(pairing_group)
                    all_member_names = "/".join(
                        [m.mention for m in all_members])
                    for member in all_members:
                        member_dm = f"Hey {member.name}!, this week for random 1-on-1s you have mattched with the following group: "\
                                + f"[{all_member_names}]. \n\n Feel free to reach out to your group directly to setup some time to get "\
                                + "to know eachother!"
                        _ = await member.send(
                            member_dm, allowed_mentions=AllowedMentions.all())

                for pairing_group in connected_components(
                        pairings.pairing_graph):
                    _ = await send_intro_dm(pairing_group)
