from .event import AbstractEvent


class AbstractChannelEvent(AbstractEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.user_id: str = raw.get('user_id')
        self.channel_id: str = raw.get('channel_id')


class JoinedChannelEvent(AbstractChannelEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.joined_at: int = raw.get('joined_at')


class ExitedChannelEvent(AbstractChannelEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.exited_at: int = raw.get('exited_at')


class UserUpdatedEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.user_id: str = raw.get('user_id')
        self.username: str = raw.get('username')
        self.avatar: str = raw.get('avatar')


class AbstractSelfGuildEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.guild_id: str = raw.get('guild_id')


class SelfJoinedGuildEvent(AbstractSelfGuildEvent):
    pass


class SelfExitedGuildEvent(AbstractSelfGuildEvent):
    pass


class MessageButtonClickEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.msg_id: str = raw.get('msg_id')
        self.user_id: str = raw.get('user_id')
        self.value: str = raw.get('value')
        self.target_id: str = raw.get('target_id')

