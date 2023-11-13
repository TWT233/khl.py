# pylint: skip-file
from typing import List

from .event import AbstractEvent


class JoinedGuildEvent(AbstractEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.user_id: str = raw.get('user_id')
        self.joined_at: int = raw.get('joined_at')


class ExitedGuildEvent(AbstractEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.user_id: str = raw.get('user_id')
        self.exited_at: int = raw.get('exited_at')


class UpdatedGuildMemberEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.user_id: str = raw.get('user_id')
        self.nickname: str = raw.get('nickname')


class AbstractGuildMemberEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.user_id: str = raw.get('user_id')
        self.event_time: int = raw.get('event_time')
        self.guilds: List[str] = raw.get('guilds')


class GuildMemberOnlineEvent(AbstractGuildMemberEvent):
    pass


class GuildMemberOfflineEvent(AbstractGuildMemberEvent):
    pass
