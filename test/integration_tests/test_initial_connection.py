import asyncio
import logging
import os
import pathlib

from discord import Client

from random1on1.api.config import config_from_json
from random1on1.random1on1bot import Random1on1Bot

logger = logging.getLogger(
    __name__)  # Note this logger does not need to log standard discord events
file_handler = logging.FileHandler(filename="test_initial_connection.log")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# IMPORTANT: To run integration tests effectively, we need to create two clients and therefore need two separate tokens (for security reasons).
#            Here the `BOT_TOKEN` is used by the `Random1on1Bot` class to run the random1on1bot program. It needs all the same permissions as the bot.
#                 the `DISCORD_TOKEN` is used by the discord.Client created for verifying the existance of proper channels.
BOT_TOKEN = os.environ["BOT_TOKEN"]
CLIENT_TOKEN = os.environ["DISCORD_TOKEN"]

TEST_CONFIG = os.environ["TEST_CONFIG"]

WORKING_DIR = pathlib.Path(__file__).parent
with open(WORKING_DIR / TEST_CONFIG, "r") as config_file:
    BOT_CONFIG = config_from_json(config_file.read())
    logger.debug("Read config from disc location %s",
                 WORKING_DIR / TEST_CONFIG)


def test_initial_connection():
    """
    Tests 
    """
    client = Client()

    bot = Random1on1Bot(token=BOT_TOKEN, config=BOT_CONFIG)
    bot.run(BOT_TOKEN)

    # TODO: Add tests here

    client.run(CLIENT_TOKEN)
