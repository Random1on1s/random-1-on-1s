import logging
from datetime import datetime

from discord import CategoryChannel
from discord import Client
from networkx import connected_components

from preconditions import preconditions

from random1on1.api.config import Random1on1BotConfig
from random1on1.api.participant import Participant
from random1on1.api.channels import AnnouncementChannel
from random1on1.api.channels import HistoryChannel
from random1on1.api.channels import LoggingChannel
from random1on1.api.config import Random1on1BotConfig
from random1on1.api.participant import Participant
from random1on1.matching.uniform import UniformMatchingAlgorithm

from threading import Thread

logger = logging.getLogger("discord")


def read_config(location):
    with open(location, "r") as config_file:
        config = Random1on1BotConfig.from_json(config_file.read())
    return config


class Random1on1Bot(Client):

    @preconditions(lambda token: len(token) > 0)
    def __init__(self, token: str, config: Random1on1BotConfig):
        super().__init__()
        self.token = token
        self.config = config
        logger.setLevel(level=logging.DEBUG)

        # TODO: Add logging handler here for writing logs to #random1on1-bot-logs channel
        # TODO: Add logging to all the elements we want

    async def on_ready(self):
        guild = self.get_guild(self.config.guild_id)
        if not guild:
            raise RuntimeError(
                f"Specified guild id: {self.config.guild_id} could not be found."
            )
        self.guild = guild

        self.category = self.get_random1on1_category()
        self.random1on1_role = self.get_random1on1_role()
        self.default_role = self.get_default_role()
        self.announcement_channel = self.get_announcement_channel()
        self.history_channel = self.get_history_channel()
        self.logging_channel = self.get_logging_channel()

    def get_random1on1_category(self) -> CategoryChannel:
        categories = []
        for channel in self.guild.channels:
            if channel.name == self.config.channel_category:
                categories.append(channel)

        if len(categories) == 0:
            category = self.guild.create_category_channel(
                name=self.config.channel_category)
        elif len(categories) == 1:
            category = categories[0]
            if not isinstance(category, CategoryChannel):
                raise RuntimeError(
                    f"Channel with name {self.config.channel_category} exists, but is not a category"
                )
        else:
            raise RuntimeError(
                f"Found multiple categories of name {self.config.channel_category}"
            )

        return category

    def get_default_role(self):
        # TODO: Change default viewer role e.g. so we can restrict that random1on1s category to people who have some sort of membership role
        return self.guild.default_role

    def get_random1on1_role(self):
        random1on1_roles = [
            r for r in self.guild.roles
            if r.name == self.config.random1on1_role
        ]
        if len(random1on1_roles) == 0:
            random1on1_role = self.guild.create_role(
                name=self.config.random1on1_role,
                mentionable=True,
                reason=
                f"Role: {self.config.random1on1_role} required for Random 1-on-1s did not exist, so I created it!",
            )
        elif len(random1on1_roles) == 1:
            random1on1_role = random1on1_roles[0]
        else:
            raise RuntimeError(
                f"Found multiple roles of name {self.config.random1on1_role}")

        return random1on1_role

    def get_announcement_channel(self) -> AnnouncementChannel:
        announcement_channel = AnnouncementChannel(
            name=self.config.announcement_channel_name, category=self.category)
        _ = announcement_channel.set_permissions(
            default_role=self.default_role,
            random1on1_role=self.random1on1_role)
        return announcement_channel

    def get_history_channel(self) -> HistoryChannel:
        history_channel = HistoryChannel(name=self.config.history_channel_name,
                                         category=self.category)
        _ = history_channel.set_permissions(
            default_role=self.default_role,
            random1on1_role=self.random1on1_role)
        return history_channel

    def get_logging_channel(self) -> LoggingChannel:
        logging_channel = LoggingChannel(name=self.config.logging_channel_name,
                                         category=self.category)
        _ = logging_channel.set_permissions(
            default_role=self.default_role,
            random1on1_role=self.random1on1_role)
        return logging_channel

    def get_participants(self) -> list[Participant]:
        participants: list[Participant] = []
        for member in self.get_random1on1_role().members:
            participants.append(Participant(member))

        return participants

    def run_matching_program(self, dry_run=False):

        participants = self.get_participants()
        previous_pairings = self.history_channel.read_historical_pairings()

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
            participants=participants, previous_pairings=previous_pairings)
        pairings = matching_algorithm.generate_pairs(dry_run=dry_run)
        _ = self.history_channel.write_pairings(pairings, dry_run=dry_run)

        if not dry_run:

            if self.config.announce_matches:
                _ = self.announcement_channel.announce_pairings(pairings)

            if self.config.dm_matches:
                bot_user = self.user
                if not bot_user:
                    raise RuntimeError(
                        "Unable to communicate with bot user required for creating pairing groups"
                    )

                pairing_channel_name = f'Random 1 on 1 pairings for {datetime.now().strftime("%Y-%m-%d")}'

                def send_intro_dm(pairing_group):
                    dm_channel = bot_user.create_group(
                        *[participant.member for participant in pairing_group])
                    _ = dm_channel.send(
                        "Hey everyone! You have been paired up this week for Random 1 on 1s! Happy chatting!"
                    )

                for pairing_group in connected_components(pairings):
                    th = Thread(target=send_intro_dm, args=(pairing_group, ))
                    th.start()
