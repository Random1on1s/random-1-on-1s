import logging

import unittest
from unittest.mock import Mock, AsyncMock
from discord import Client, TextChannel

from random1on1.api.discord_handler import DiscordClientHandler

class TestDiscordHandler(unittest.TestCase):

    def test_emit(self):
        msg_log = set()
        channels = [10, 17, 202]
        msg = 'hello'

        # configure mock channels
        channel_mocks = {}
        for channel_id in channels:
            channel = Mock(TextChannel)
            channel.send = AsyncMock(
                    side_effect=lambda msg,c_id=channel_id : msg_log.add((c_id, msg))
            )
            channel_mocks[channel_id] = channel

        # configure mock click
        mock_client = Mock(Client)
        mock_client.fetch_channel = AsyncMock(
                side_effect=lambda c_id : channel_mocks[c_id]
        )

        # configure handler
        logger = logging.getLogger(__name__)
        handler = DiscordClientHandler(mock_client, channels)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.info(msg)

        # perform tests
        for channel_id in channels:
            self.assertTrue((channel_id, msg) in msg_log)

if __name__ == '__main__':
    unittest.main()
