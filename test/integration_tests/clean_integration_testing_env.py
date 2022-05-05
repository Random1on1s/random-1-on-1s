import logging
import os
import pathlib

from discord import Client

from random1on1.api.config import config_from_json

TEST_CONFIG = os.environ["TEST_CONFIG"]
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
WORKING_DIR = pathlib.Path(__file__).parent

logger = logging.getLogger(
    __name__
)  # Note: we do not want to include discord logs for this script, generally speaking
file_handler = logging.FileHandler(
    filename='clean_integration_testing_env.log')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

client = Client()

with open(WORKING_DIR / TEST_CONFIG, "r") as config_file:
    config = config_from_json(config_file.read())
    logger.debug("Read config from disc location %s",
                 WORKING_DIR / TEST_CONFIG)


@client.event
async def on_ready():
    guild = await client.fetch_guild(config.guild_id)

    for role in guild.roles:
        if role.name == config.random1on1_role:
            logger.debug("Deleting testing role %s", role.name)
            _ = await role.delete(reason=f"Deleting testing role {role.name}")

    for category in guild.categories:
        if category.name == config.channel_category:
            channels_to_delete = set([
                config.announcement_channel, config.history_channel,
                config.logging_channel
            ])
            for channel in category.channels:
                if channel.name in channels_to_delete:
                    logger.debug("Deleting testing channel %s", channel.name)
                    _ = await channel.delete(
                        reason=f"Deleting testing channel {channel.name}")

            logger.debug("Deleting testing category %s", category.name)
            _ = await category.delete(
                reason=f"Delenting testing category {category.name}")

    logger.debug(
        "Completed cleaning for integraiotn testing server. Closing client")
    _ = await client.close()


client.run(DISCORD_TOKEN)
