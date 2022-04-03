from discord import Client
import logging
from random1on1.api.config import Random1on1BotConfig

logger = logging.getLogger("discord")


def read_config(location):
    with open(location, "r") as config_file:
        config = Random1on1BotConfig.from_json(config_file.read())
    return config


class Random1on1Bot(Client):

    def __init__(self, *args, **kwargs):
        # TODO: Figure out which items to go in constructor: config, token ?
        super().__init__(*args, **kwargs)
        logger.setLevel(level=logging.DEBUG)
        # TODO: Add logging handler here for writing logs to #random1on1-bot-logs channel

    async def on_ready(self):
        # TODO: Ensure that channels required exist
        # TODO: Ensure that you can read history from soemwhere
        # TODO: Ensure that you can retrieve the list of participants
        # TODO: Ensure that you can send messages to individual participants
        # TODO: Ensure that you can send messages to the proper channels
        raise NotImplementedError()

    def generate_pairs(self):
        # TODO: Generate the pairs according to proper algorithm
        raise NotImplementedError()

    def log_pairings(self, pairings, dry_run=False):
        # TODO: Log pairings in proper channel
        raise NotImplementedError()

    def send_pairings(self, pairings, dry_run=False):
        # TODO: Send out pairings
        raise NotImplementedError()

    def run_matching_program(self, dry_run=False):
        # TODO: Run matching program in full
        raise NotImplementedError()
