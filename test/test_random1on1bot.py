import pytest

import discord  # This import is needed in order for pytest mocking to work, please don't remove

from preconditions import PreconditionError

from random1on1.random1on1bot import Random1on1Bot
from random1on1.api.config import Random1on1BotConfig

TEST_TOKEN = "test_token"
TEST_GUILD_ID = "test_guild_id"


class TestRandom1on1Bot:

    @pytest.fixture
    def create_default_bot(self):
        config = Random1on1BotConfig(guild_id=TEST_GUILD_ID)
        return Random1on1Bot(token=TEST_TOKEN, config=config)

    def test_empty_token(self):
        with pytest.raises(PreconditionError):
            Random1on1Bot(token="",
                          config=Random1on1BotConfig(guild_id=TEST_GUILD_ID))

    def test_category_creation_no_existing_categorys(self, mocker):
        bot = self.create_default_bot()
        mocker.patch('bot.guild.channels', [])
        channel_created = mocker.patch('discord.CategoryChannel')
        channel_created.name = bot.config.channel_category
        mocker.patch('bot.guild.create_category_channel', channel_created)
        category = bot.get_random1on1_category()
        assert category.name == bot.config.channel_category

    def test_category_creation_no_existing_categories_same_name(self, mocker):
        bot = self.create_default_bot()
        existing_category_different_name = mocker.patch(
            'discord.CategoryChannel')
        existing_category_different_name.name = 'different_name'
        mocker.patch('bot.guild.channels', [existing_category_different_name])
        category = bot.get_random1on1_category()
        assert category.name == bot.config.channel_category

    def test_category_creation_existing_categories_same_name(self, mocker):
        bot = self.create_default_bot()
        existing_category_same_name = mocker.patch('discord.CategoryChannel')
        existing_category_same_name.name = bot.config.channel_category
        mocker.patch('bot.guild.channels', [existing_category_same_name])
        category = bot.get_random1on1_category()
        assert category.name == bot.config.channel_category
        assert category == existing_category_same_name

    def test_category_creation_multiple_existing_categories_same_name(
            self, mocker):
        bot = self.create_default_bot()
        existing_category_same_name_1 = mocker.patch('discord.CategoryChannel')
        existing_category_same_name_1.name = bot.config.channel_category
        existing_category_same_name_2 = mocker.patch('discord.CategoryChannel')
        existing_category_same_name_2.name = bot.config.channel_category
        mocker.patch(
            'bot.guild.channels',
            [existing_category_same_name_1, existing_category_same_name_2])
        with pytest.raises(RuntimeError):
            bot.get_random1on1_category()

    def test_role_creation_no_existing_roles(self, mocker):
        bot = self.create_default_bot()
        mocker.patch('bot.guild.roles', [])
        role_created = mocker.patch('discord.Role')
        role_created.name = bot.config.random1on1_role
        mocker.patch('bot.guild.create_role', role_created)
        role = bot.get_random1on1_role()
        assert role.name == bot.config.random1on1_role

    def test_role_creation_no_existing_categories_same_name(self, mocker):
        bot = self.create_default_bot()
        existing_role_different_name = mocker.patch('discord.Role')
        existing_role_different_name.name = 'different_name'
        mocker.patch('bot.guild.roles', [existing_role_different_name])
        role = bot.get_random1on1_role()
        assert role.name == bot.config.random1on1_role

    def test_role_creation_existing_categories_same_name(self, mocker):
        bot = self.create_default_bot()
        existing_role_same_name = mocker.patch('discord.Role')
        existing_role_same_name.name = bot.config.random1on1_role
        mocker.patch('bot.guild.roles', [existing_role_same_name])
        role = bot.get_random1on1_role()
        assert role.name == bot.config.random1on1_role
        assert role == existing_role_same_name

    def test_role_creation_multiple_existing_categories_same_name(
            self, mocker):
        bot = self.create_default_bot()
        existing_role_same_name_1 = mocker.patch('discord.Role')
        existing_role_same_name_1.name = bot.config.random1on1_role
        existing_role_same_name_2 = mocker.patch('discord.Role')
        existing_role_same_name_2.name = bot.config.random1on1_role
        mocker.patch('bot.guild.roles',
                     [existing_role_same_name_1, existing_role_same_name_2])
        with pytest.raises(RuntimeError):
            bot.get_random1on1_role()

    def test_channel_creation(self):
        bot = self.create_default_bot()
        announcement_channel = bot.get_announcement_channel()
        history_channel = bot.get_history_channel()
        logging_channel = bot.get_logging_channel()

        assert announcement_channel is not None
        assert announcement_channel.name == bot.config.announcement_channel_name

        assert history_channel is not None
        assert history_channel.name == bot.config.history_channel_name

        assert logging_channel is not None
        assert logging_channel.name == bot.config.logging_channel_name

    def test_get_participants(self, mocker):
        bot = self.create_default_bot()

        mock_role = mocker.patch("discord.Role")
        mock_role.name = bot.config.random1on1_role
        participant_1 = mocker.patch("discord.Member")
        participant_1.roles = [mock_role]
        mock_role.members = [participant_1]
        mocker.patch("bot.guild.roles", [mock_role])

        list_of_participants = bot.get_participants()
        assert len(list_of_participants) == 1
        assert list_of_participants[0] == participant_1
