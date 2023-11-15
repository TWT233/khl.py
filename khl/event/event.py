# pylint: skip-file
from abc import ABC
from typing import List

from .interface import BaseEvent
from .. import Role


class TypedEvent:
    class Channel:
        class _BaseReactionEvent(BaseEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.user_id: str = raw.get('user_id')
                self.channel_id: str = raw.get('channel_id')
                self.emoji: dict = raw.get('emoji')

        class AddedReaction(_BaseReactionEvent):
            pass

        class DeletedReaction(_BaseReactionEvent):
            pass

        class UpdatedMessage(BaseEvent):
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

        class DeletedMessage(BaseEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.channel_id: str = raw.get('channel_id')

        class AddedChannel(BaseEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.channel: dict = raw

        class DeletedChannel(BaseEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.id: str = raw.get('id')
                self.deleted_at: int = raw.get('deleted_at')

        class _BasePinEvent(BaseEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.channel_id: str = raw.get('channel_id')
                self.operator_id: str = raw.get('operator_id')
                self.msg_id: str = raw.get('msg_id')

        class PinnedMessage(_BasePinEvent):
            pass

        class UnpinnedMessage(_BasePinEvent):
            pass

    class Guild:
        class _BaseGuildEvent(BaseEvent, ABC):
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

        class UpdateGuild(_BaseGuildEvent):
            pass

        class DeleteGuild(_BaseGuildEvent):
            pass

        class _BaseBlockListEvent(BaseEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.operator_id: str = raw.get('operator_id')
                self.user_id: List[str] = raw.get('user_id')

        class AddedBlockList(_BaseBlockListEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.remark: str = raw.get('remark')

        class DeleteBlockList(_BaseBlockListEvent):
            pass

        class _BaseEmojiEvent(BaseEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.id: str = raw.get('id')
                self.name: str = raw.get('name')

        class AddedEmoji(_BaseEmojiEvent):
            pass

        class DeletedEmoji(_BaseEmojiEvent):
            pass

        class UpdateEmoji(_BaseEmojiEvent):
            pass

    class GuildRole:
        class _BaseRoleEvent(BaseEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.role = Role(**raw)

        class AddedRole(_BaseRoleEvent):
            pass

        class DeleteRole(_BaseRoleEvent):
            pass

        class UpdateRole(_BaseRoleEvent):
            pass

    class GuildUser:
        class JoinedGuild(BaseEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.joined_at: int = raw.get('joined_at')

        class ExitedGuild(BaseEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.exited_at: int = raw.get('exited_at')

        class UpdatedGuildMember(BaseEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.nickname: str = raw.get('nickname')

        class _BaseGuildMemberEvent(BaseEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.event_time: int = raw.get('event_time')
                self.guilds: List[str] = raw.get('guilds')

        class GuildMemberOnline(_BaseGuildMemberEvent):
            pass

        class GuildMemberOffline(_BaseGuildMemberEvent):
            pass

    class PrivateMessage:
        class _BasePrivateMessageEvent(BaseEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.author_id: str = raw.get('author_id')
                self.target_id: str = raw.get('target_id')
                self.chat_code: str = raw.get('chat_code')

        class UpdatePrivateMessage(_BasePrivateMessageEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.content: str = raw.get('content')
                self.updated_at: int = raw.get('updated_at')

        class DeletedPrivateMessage(_BasePrivateMessageEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.deleted_at: int = raw.get('deleted_at')

        class _BasePrivateReactionEvent(BaseEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.user_id: str = raw.get('user_id')
                self.channel_id: str = raw.get('channel_id')
                self.emoji: dict = raw.get('emoji')
                self.chat_code: str = raw.get('chat_code')

        class PrivateAddedReaction(_BasePrivateReactionEvent):
            pass

        class PrivateDeletedReaction(_BasePrivateReactionEvent):
            pass

    class User:
        class _BaseChannelEvent(BaseEvent, ABC):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.channel_id: str = raw.get('channel_id')

        class JoinedChannel(_BaseChannelEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.joined_at: int = raw.get('joined_at')

        class ExitedChannel(_BaseChannelEvent):
            def __init__(self, raw: dict):
                super().__init__(raw)
                self.exited_at: int = raw.get('exited_at')

        class UserUpdated(BaseEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.user_id: str = raw.get('user_id')
                self.username: str = raw.get('username')
                self.avatar: str = raw.get('avatar')

        class _BaseSelfGuildEvent(BaseEvent, ABC):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.guild_id: str = raw.get('guild_id')

        class SelfJoinedGuild(_BaseSelfGuildEvent):
            pass

        class SelfExitedGuild(_BaseSelfGuildEvent):
            pass

        class MessageButtonClick(BaseEvent):

            def __init__(self, raw: dict):
                super().__init__(raw)
                self.msg_id: str = raw.get('msg_id')
                self.user_id: str = raw.get('user_id')
                self.value: str = raw.get('value')
                self.target_id: str = raw.get('target_id')
