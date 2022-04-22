import asyncio

from typing import List
from logging import Handler, NOTSET, LogRecord
from discord import Client, TextChannel


class DiscordClientHandler(Handler):

    def __init__(self,
                 discord_client: Client,
                 channels: List[int],
                 level=NOTSET):
        super().__init__(level)
        self.discord_client = discord_client
        self.channels = channels

    def emit(self, record: LogRecord):
        try:
            msg = self.format(record)
            asyncio.run(self.async_emit_helper(msg))
        except Exception as e:
            self.handleError(record)

    async def async_emit_helper(self, msg):
        tasks = []
        for channel_id in self.channels:
            tasks.append(
                asyncio.create_task(self.async_send_message(channel_id, msg)))
        for task in tasks:
            await task

    async def async_send_message(self, channel_id: int, msg: str):
        channel = await self.discord_client.fetch_channel(channel_id)
        assert isinstance(channel, TextChannel)
        await channel.send(msg)
