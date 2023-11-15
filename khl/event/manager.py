import asyncio
import inspect
import logging
from typing import Callable, Coroutine, Any, Dict, Type, List, Optional, Union

from .event import TypedEvent
from .interface import BaseEvent
from .. import Event, EventTypes

log = logging.getLogger(__name__)

TypeTypedEventHandle = Callable[[BaseEvent], Coroutine[Any, Any, None]]

_EVENT_MAP = {
    EventTypes.ADDED_REACTION: TypedEvent.Channel.AddedReaction,
    EventTypes.DELETED_REACTION: TypedEvent.Channel.DeletedReaction,
    EventTypes.UPDATED_MESSAGE: TypedEvent.Channel.UpdatedMessage,
    EventTypes.MESSAGE_UPDATED: TypedEvent.Channel.UpdatedMessage,
    EventTypes.DELETED_MESSAGE: TypedEvent.Channel.DeletedMessage,
    EventTypes.ADDED_CHANNEL: TypedEvent.Channel.AddedChannel,
    EventTypes.DELETED_CHANNEL: TypedEvent.Channel.DeletedChannel,
    EventTypes.PINNED_MESSAGE: TypedEvent.Channel.PinnedMessage,
    EventTypes.UNPINNED_MESSAGE: TypedEvent.Channel.UnpinnedMessage,
    EventTypes.UPDATED_PRIVATE_MESSAGE: TypedEvent.PrivateMessage.UpdatePrivateMessage,
    EventTypes.DELETED_PRIVATE_MESSAGE: TypedEvent.PrivateMessage.DeletedPrivateMessage,
    EventTypes.PRIVATE_ADDED_REACTION: TypedEvent.PrivateMessage.PrivateAddedReaction,
    EventTypes.PRIVATE_DELETED_REACTION: TypedEvent.PrivateMessage.PrivateDeletedReaction,
    EventTypes.JOINED_GUILD: TypedEvent.GuildUser.JoinedGuild,
    EventTypes.EXITED_GUILD: TypedEvent.GuildUser.ExitedGuild,
    EventTypes.UPDATED_GUILD_MEMBER: TypedEvent.GuildUser.UpdatedGuildMember,
    EventTypes.GUILD_MEMBER_ONLINE: TypedEvent.GuildUser.GuildMemberOnline,
    EventTypes.GUILD_MEMBER_OFFLINE: TypedEvent.GuildUser.GuildMemberOffline,
    EventTypes.ADDED_ROLE: TypedEvent.GuildRole.AddedRole,
    EventTypes.DELETED_ROLE: TypedEvent.GuildRole.DeleteRole,
    EventTypes.UPDATED_ROLE: TypedEvent.GuildRole.UpdateRole,
    EventTypes.UPDATED_GUILD: TypedEvent.Guild.UpdateGuild,
    EventTypes.DELETED_GUILD: TypedEvent.Guild.DeleteGuild,
    EventTypes.ADDED_BLOCK_LIST: TypedEvent.Guild.AddedBlockList,
    EventTypes.DELETED_BLOCK_LIST: TypedEvent.Guild.DeleteBlockList,
    EventTypes.ADDED_EMOJI: TypedEvent.Guild.AddedEmoji,
    EventTypes.DELETED_EMOJI: TypedEvent.Guild.DeletedEmoji,
    EventTypes.UPDATED_EMOJI: TypedEvent.Guild.UpdateEmoji,
    EventTypes.JOINED_CHANNEL: TypedEvent.User.JoinedChannel,
    EventTypes.EXITED_CHANNEL: TypedEvent.User.ExitedChannel,
    EventTypes.USER_UPDATED: TypedEvent.User.UserUpdated,
    EventTypes.SELF_JOINED_GUILD: TypedEvent.User.SelfJoinedGuild,
    EventTypes.SELF_EXITED_GUILD: TypedEvent.User.SelfExitedGuild,
    EventTypes.MESSAGE_BTN_CLICK: TypedEvent.User.MessageButtonClick
}


class EventManager:
    """Register and post events"""

    def __call__(self, handle: TypeTypedEventHandle):
        self.subscribe(handle)

    def __init__(self):
        self._event_handles: Dict[Type[BaseEvent], List[TypeTypedEventHandle]] = {}

    async def post(self, event: Union[BaseEvent, Event]):
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

    def subscribe(self, handle: TypeTypedEventHandle):
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
        if not issubclass(event_type, BaseEvent):
            log.error('Event handle %s type not match.', name)
            return

        if event_type not in self._event_handles:
            self._event_handles[event_type] = []
        self._event_handles[event_type].append(handle)

        log.debug('Event handle %s registered.', name)

    @staticmethod
    def _make_event(event: Event) -> Optional[BaseEvent]:
        """make event to typed event"""
        event_type = event.event_type

        cls = _EVENT_MAP.get(event_type, None)

        if cls:
            return cls(event.body)
        return None
