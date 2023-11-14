import asyncio
import inspect
import logging
from typing import Callable, Coroutine, Any, Dict, Type, List, Optional, Union

from .event import TypedEvent
from .interface import AbstractEvent
from .. import Event, EventTypes

log = logging.getLogger(__name__)

EVENT_HANDLE_TYPE = Callable[[AbstractEvent], Coroutine[Any, Any, None]]

_EVENT_MAP = {
    EventTypes.ADDED_REACTION: TypedEvent.ChannelEvent.AddedReactionEvent,
    EventTypes.DELETED_REACTION: TypedEvent.ChannelEvent.DeletedReactionEvent,
    EventTypes.UPDATED_MESSAGE: TypedEvent.ChannelEvent.UpdatedMessageEvent,
    EventTypes.MESSAGE_UPDATED: TypedEvent.ChannelEvent.UpdatedMessageEvent,
    EventTypes.DELETED_MESSAGE: TypedEvent.ChannelEvent.DeletedMessageEvent,
    EventTypes.ADDED_CHANNEL: TypedEvent.ChannelEvent.AddedChannelEvent,
    EventTypes.DELETED_CHANNEL: TypedEvent.ChannelEvent.DeletedChannelEvent,
    EventTypes.PINNED_MESSAGE: TypedEvent.ChannelEvent.PinnedMessageEvent,
    EventTypes.UNPINNED_MESSAGE: TypedEvent.ChannelEvent.UnpinnedMessageEvent,
    EventTypes.UPDATED_PRIVATE_MESSAGE: TypedEvent.PrivateMessageEvent.UpdatePrivateMessageEvent,
    EventTypes.DELETED_PRIVATE_MESSAGE: TypedEvent.PrivateMessageEvent.DeletedPrivateMessageEvent,
    EventTypes.PRIVATE_ADDED_REACTION: TypedEvent.PrivateMessageEvent.PrivateAddedReactionEvent,
    EventTypes.PRIVATE_DELETED_REACTION: TypedEvent.PrivateMessageEvent.PrivateDeletedReactionEvent,
    EventTypes.JOINED_GUILD: TypedEvent.GuildUserEvent.JoinedGuildEvent,
    EventTypes.EXITED_GUILD: TypedEvent.GuildUserEvent.ExitedGuildEvent,
    EventTypes.UPDATED_GUILD_MEMBER: TypedEvent.GuildUserEvent.UpdatedGuildMemberEvent,
    EventTypes.GUILD_MEMBER_ONLINE: TypedEvent.GuildUserEvent.GuildMemberOnlineEvent,
    EventTypes.GUILD_MEMBER_OFFLINE: TypedEvent.GuildUserEvent.GuildMemberOfflineEvent,
    EventTypes.ADDED_ROLE: TypedEvent.GuildRoleEvent.AddedRoleEvent,
    EventTypes.DELETED_ROLE: TypedEvent.GuildRoleEvent.DeleteRoleEvent,
    EventTypes.UPDATED_ROLE: TypedEvent.GuildRoleEvent.UpdateRoleEvent,
    EventTypes.UPDATED_GUILD: TypedEvent.GuildEvent.UpdateGuildEvent,
    EventTypes.DELETED_GUILD: TypedEvent.GuildEvent.DeleteGuildEvent,
    EventTypes.ADDED_BLOCK_LIST: TypedEvent.GuildEvent.AddedBlockListEvent,
    EventTypes.DELETED_BLOCK_LIST: TypedEvent.GuildEvent.DeleteBlockListEvent,
    EventTypes.ADDED_EMOJI: TypedEvent.GuildEvent.AddedEmojiEvent,
    EventTypes.DELETED_EMOJI: TypedEvent.GuildEvent.DeletedEmojiEvent,
    EventTypes.UPDATED_EMOJI: TypedEvent.GuildEvent.UpdateEmojiEvent,
    EventTypes.JOINED_CHANNEL: TypedEvent.UserEvent.JoinedChannelEvent,
    EventTypes.EXITED_CHANNEL: TypedEvent.UserEvent.ExitedChannelEvent,
    EventTypes.USER_UPDATED: TypedEvent.UserEvent.UserUpdatedEvent,
    EventTypes.SELF_JOINED_GUILD: TypedEvent.UserEvent.SelfJoinedGuildEvent,
    EventTypes.SELF_EXITED_GUILD: TypedEvent.UserEvent.SelfExitedGuildEvent,
    EventTypes.MESSAGE_BTN_CLICK: TypedEvent.UserEvent.MessageButtonClickEvent
}


class EventManager:
    """Register and post events"""

    def __call__(self, handle: EVENT_HANDLE_TYPE):
        self.subscribe(handle)

    def __init__(self):
        self._event_handles: Dict[Type[AbstractEvent], List[EVENT_HANDLE_TYPE]] = {}

    async def post(self, event: Union[AbstractEvent, Event]):
        """post event to registered handles"""
        if isinstance(event, Event):
            event = self._make_event(event)
        for handle in self._event_handles.get(event.__class__, []):
            try:
                await handle(event)
            except Exception as e:
                log.exception(
                    'error raised during event %s handling in %s', event.__class__, handle.__name__,
                    exc_info=e
                )

    def subscribe(self, handle: EVENT_HANDLE_TYPE):
        """subscribe an event"""
        name = handle.__name__
        if not asyncio.iscoroutinefunction(handle):
            log.error('Event handle %s is not coroutine function.', name)
            return

        sig = inspect.signature(handle)
        params = list(sig.parameters.values())
        if len(params) != 1:
            log.error('Event handle %s params lens not match.', name)
            return
        event_type = params[0].annotation
        if not issubclass(event_type, AbstractEvent):
            log.error('Event handle %s type not match.', name)
            return

        if event_type not in self._event_handles:
            self._event_handles[event_type] = []
        self._event_handles[event_type].append(handle)

        log.debug('Event handle %s registered.', name)

    @staticmethod
    def _make_event(event: Event) -> Optional[AbstractEvent]:
        """make event to typed event"""
        event_type = event.event_type

        cls = _EVENT_MAP.get(event_type, None)

        if cls:
            return cls(event.body)
        return None
