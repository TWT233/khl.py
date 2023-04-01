"""type enums"""
from enum import IntEnum, Enum
from typing import Dict, Any


class MessageTypes(IntEnum):
    """
    types of message, type==SYS will be interpreted as `Event`, others are `Message`
    """
    TEXT = 1
    IMG = 2
    VIDEO = 3
    FILE = 4
    AUDIO = 8
    KMD = 9
    CARD = 10
    SYS = 255


class ChannelTypes(IntEnum):
    """
    types of channel
    """
    CATEGORY = 0
    TEXT = 1
    VOICE = 2


class ChannelPrivacyTypes(Enum):
    """
    channel's privacy level
    """
    GROUP = 'GROUP'
    PERSON = 'PERSON'


class EventTypes(Enum):
    """
    for system events(type==255)
    """
    MESSAGE_BTN_CLICK = 'message_btn_click'

    ADDED_REACTION = 'added_reaction'
    DELETED_REACTION = 'deleted_reaction'
    UPDATED_MESSAGE = 'updated_message'
    DELETED_MESSAGE = 'deleted_message'
    MESSAGE_UPDATED = 'message_updated'

    PRIVATE_ADDED_REACTION = 'private_added_reaction'
    PRIVATE_DELETED_REACTION = 'private_deleted_reaction'
    UPDATED_PRIVATE_MESSAGE = 'updated_private_message'
    DELETED_PRIVATE_MESSAGE = 'deleted_private_message'

    UPDATED_GUILD = 'updated_guild'
    DELETED_GUILD = 'deleted_guild'
    ADDED_BLOCK_LIST = 'added_block_list'
    DELETED_BLOCK_LIST = 'deleted_block_list'

    ADDED_ROLE = 'added_role'
    DELETED_ROLE = 'deleted_role'
    UPDATED_ROLE = 'updated_role'

    JOINED_GUILD = 'joined_guild'
    EXITED_GUILD = 'exited_guild'
    GUILD_MEMBER_ONLINE = 'guild_member_online'
    GUILD_MEMBER_OFFLINE = 'guild_member_offline'

    UPDATED_GUILD_MEMBER = 'updated_guild_member'

    UPDATED_CHANNEL = 'updated_channel'
    ADDED_CHANNEL = 'added_channel'
    DELETED_CHANNEL = 'deleted_channel'

    JOINED_CHANNEL = 'joined_channel'
    EXITED_CHANNEL = 'exited_channel'
    USER_UPDATED = 'user_updated'
    SELF_JOINED_GUILD = 'self_joined_guild'
    SELF_EXITED_GUILD = 'self_exited_guild'

    PINNED_MESSAGE = 'pinned_message'
    UNPINNED_MESSAGE = 'unpinned_message'

    ADDED_EMOJI = 'added_emoji'
    DELETED_EMOJI = 'deleted_emoji'
    UPDATED_EMOJI = 'updated_emoji'


class GuildMuteTypes(IntEnum):
    """
    types of guild-mute
    """
    MIC = 1
    HEADSET = 2


class SlowModeTypes(IntEnum):
    """
    types of slow mode
    """
    FIVE_SEC = 5000
    TEN_SEC = 10000
    FIFTEEN_SEC = 15000
    THIRTY_SEC = 30000
    ONE_MIN = 60000
    TWO_MIN = 120000
    FIVE_MIN = 300000
    TEN_MIN = 600000
    FIFTEEN_MIN = 900000
    THIRTY_MIN = 1800000
    ONE_HOUR = 3600000
    TWO_HOUR = 7200000
    SIX_HOUR = 21600000

    @classmethod
    def possible_value(cls) -> Dict[Any, Enum]:
        """returns a dict with all enum names and corresponding values"""
        return cls._value2member_map_  # pylint: disable=no-member


class RoleTypes(IntEnum):
    """
    types of role type
    """
    UserCreated = 0
    BotSpecified = 1
    Booster = 2
    Everyone = 255


class SoftwareTypes(Enum):
    """types of listening music used software"""
    CLOUD_MUSIC = "cloudmusic"
    QQ_MUSIC = "qqmusic"
    KUGOU_MUSIC = "kugou"


class BadgeTypes(IntEnum):
    """types of guild badges"""
    NAME = 0
    ONLINE = 1
    ONLINE_MAX = 2


class MessageFlagModes(Enum):
    """types of message flag mode"""
    BEFORE = 'before'
    AFTER = 'after'
    AROUND = 'around'


class GameTypes(Enum):
    """types of games"""
    ALL = '0'
    USER_CREATED = '1'
    SYSTEM_CREATED = '2'


class FriendTypes(Enum):
    """types of friends"""
    REQUEST = "request"
    FRIEND = "friend"
    BLOCKED = "blocked"
