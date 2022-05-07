import pytest

from random1on1.api.config import config_from_json
from random1on1.api.config import Random1on1BotConfig

EMPTY_CONFIG_STR = '{}'
TEST_CONFIG_STR = '{ "guild_id": 1, "dm_matches": false, "announce_matches": true, "history_channel": "hist"}'


def test_config_validation():
    with pytest.raises(ValueError):
        _ = Random1on1BotConfig(guild_id=1,
                                announce_matches=False,
                                dm_matches=False)


def test_config_deserialization_missing_guild():
    with pytest.raises(ValueError):
        _ = config_from_json(EMPTY_CONFIG_STR)


def test_config_deserialization_proper_config():
    test_config = config_from_json(TEST_CONFIG_STR)
    assert test_config.guild_id == 1
    assert test_config.dm_matches == False
    assert test_config.announce_matches == True
    assert test_config.history_channel == "hist"
