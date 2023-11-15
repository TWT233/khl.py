# pylint: skip-file
from abc import ABC
from typing import List

from .interface import AbstractEvent
from .. import Role


class TypedEvent:
    class Channel:
        class _AbstractReactionEvent(AbstractEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.user_id: str = raw.get('user_id')
                self.channel_id: str = raw.get('channel_id')
                self.emoji: dict = raw.get('emoji')

        class AddedReaction(_AbstractReactionEvent):
            pass

        class DeletedReaction(_AbstractReactionEvent):
            pass

        class UpdatedMessage(AbstractEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.content: str = raw.get('content')
                self.channel_id: str = raw.get('channel_id')
                self.mention: List[str] = raw.get('mention')
                self.mention_all: bool = raw.get('mention_all')
                self.mention_here: bool = raw.get('mention_here')
                self.mention_roles: List[int] = raw.get('mention_roles')
                self.updated_at: int = raw.get('updated_at')

        class DeletedMessage(AbstractEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.channel_id: str = raw.get('channel_id')

        class AddedChannel(AbstractEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.channel: dict = raw

        class DeletedChannel(AbstractEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.id: str = raw.get('id')
                self.deleted_at: int = raw.get('deleted_at')

        class _AbstractPinEvent(AbstractEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.channel_id: str = raw.get('channel_id')
                self.operator_id: str = raw.get('operator_id')
                self.msg_id: str = raw.get('msg_id')

        class PinnedMessage(_AbstractPinEvent):
            pass

        class UnpinnedMessage(_AbstractPinEvent):
            pass

    class Guild:
        class _AbstractGuildEvent(AbstractEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.id: str = raw.get('id')
                self.name: str = raw.get('name')
                self.user_id: str = raw.get('user_id')
                self.icon: str = raw.get('icon')
                self.notify_type: int = raw.get('notify_type')
                self.region: str = raw.get('region')
                self.enable_open: int = raw.get('enable_open')
                self.open_id: int = raw.get('open_id')
                self.default_channel_id: str = raw.get('default_channel_id')
                self.welcome_channel_id: str = raw.get('welcome_channel_id')

        class UpdateGuild(_AbstractGuildEvent):
            pass

        class DeleteGuild(_AbstractGuildEvent):
            pass

        class _AbstractBlockListEvent(AbstractEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.operator_id: str = raw.get('operator_id')
                self.user_id: List[str] = raw.get('user_id')

        class AddedBlockList(_AbstractBlockListEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.remark: str = raw.get('remark')

        class DeleteBlockList(_AbstractBlockListEvent):
            pass

        class _AbstractEmojiEvent(AbstractEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.id: str = raw.get('id')
                self.name: str = raw.get('name')

        class AddedEmoji(_AbstractEmojiEvent):
            pass

        class DeletedEmoji(_AbstractEmojiEvent):
            pass

        class UpdateEmoji(_AbstractEmojiEvent):
            pass

    class GuildRole:
        class _AbstractRoleEvent(AbstractEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.role = Role(**raw)

        class AddedRole(_AbstractRoleEvent):
            pass

        class DeleteRole(_AbstractRoleEvent):
            pass

        class UpdateRole(_AbstractRoleEvent):
            pass

    class GuildUser:
        class JoinedGuild(AbstractEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.joined_at: int = raw.get('joined_at')

        class ExitedGuild(AbstractEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.exited_at: int = raw.get('exited_at')

        class UpdatedGuildMember(AbstractEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.nickname: str = raw.get('nickname')

        class _AbstractGuildMemberEvent(AbstractEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.event_time: int = raw.get('event_time')
                self.guilds: List[str] = raw.get('guilds')

        class GuildMemberOnline(_AbstractGuildMemberEvent):
            pass

        class GuildMemberOffline(_AbstractGuildMemberEvent):
            pass

    class PrivateMessage:
        class _AbstractPrivateMessageEvent(AbstractEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.author_id: str = raw.get('author_id')
                self.target_id: str = raw.get('target_id')
                self.chat_code: str = raw.get('chat_code')

        class UpdatePrivateMessage(_AbstractPrivateMessageEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.content: str = raw.get('content')
                self.updated_at: int = raw.get('updated_at')

        class DeletedPrivateMessage(_AbstractPrivateMessageEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.deleted_at: int = raw.get('deleted_at')

        class _AbstractPrivateReactionEvent(AbstractEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.user_id: str = raw.get('user_id')
                self.channel_id: str = raw.get('channel_id')
                self.emoji: dict = raw.get('emoji')
                self.chat_code: str = raw.get('chat_code')

        class PrivateAddedReaction(_AbstractPrivateReactionEvent):
            pass

        class PrivateDeletedReaction(_AbstractPrivateReactionEvent):
            pass

    class User:
        class _AbstractChannelEvent(AbstractEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.channel_id: str = raw.get('channel_id')

        class JoinedChannel(_AbstractChannelEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.joined_at: int = raw.get('joined_at')

        class ExitedChannel(_AbstractChannelEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.exited_at: int = raw.get('exited_at')

        class UserUpdated(AbstractEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.username: str = raw.get('username')
                self.avatar: str = raw.get('avatar')

        class _AbstractSelfGuildEvent(AbstractEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.guild_id: str = raw.get('guild_id')

        class SelfJoinedGuild(_AbstractSelfGuildEvent):
            pass

        class SelfExitedGuild(_AbstractSelfGuildEvent):
            pass

        class MessageButtonClick(AbstractEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.user_id: str = raw.get('user_id')
                self.value: str = raw.get('value')
                self.target_id: str = raw.get('target_id')
