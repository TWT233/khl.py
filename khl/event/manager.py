import asyncio
import inspect
import logging
from typing import Callable, Coroutine, Any, Dict, Type, List, Optional

from .events.event import AbstractEvent
from .events.channel_events import AddedReactionEvent, DeletedReactionEvent, UpdatedMessageEvent, DeletedMessageEvent, \
    AddedChannelEvent, DeletedChannelEvent, PinnedMessageEvent, UnpinnedMessageEvent
from .events.guild_events import UpdateGuildEvent, DeleteGuildEvent, AddedBlockListEvent, DeleteBlockListEvent, \
    AddedEmojiEvent, DeletedEmojiEvent, UpdateEmojiEvent
from .events.guild_role_events import AddedRoleEvent, DeleteRoleEvent, UpdateRoleEvent
from .events.guild_user_events import JoinedGuildEvent, ExitedGuildEvent, UpdatedGuildMemberEvent, \
    GuildMemberOnlineEvent, GuildMemberOfflineEvent
from .events.private_message_events import UpdatePrivateMessageEvent, DeletedPrivateMessageEvent, \
    PrivateAddedReactionEvent, PrivateDeletedReactionEvent
from .events.user_events import JoinedChannelEvent, ExitedChannelEvent, UserUpdatedEvent, SelfJoinedGuildEvent, \
    SelfExitedGuildEvent, MessageButtonClickEvent

from .. import Event, EventTypes

log = logging.getLogger(__name__)

EVENT_HANDLE_TYPE = Callable[[AbstractEvent], Coroutine[Any, Any, None]]

_EVENT_MAP = {
    EventTypes.ADDED_REACTION: AddedReactionEvent,
    EventTypes.DELETED_REACTION: DeletedReactionEvent,
    EventTypes.UPDATED_MESSAGE: UpdatedMessageEvent,
    EventTypes.MESSAGE_UPDATED: UpdatedMessageEvent,
    EventTypes.DELETED_MESSAGE: DeletedMessageEvent,
    EventTypes.ADDED_CHANNEL: AddedChannelEvent,
    EventTypes.DELETED_CHANNEL: DeletedChannelEvent,
    EventTypes.PINNED_MESSAGE: PinnedMessageEvent,
    EventTypes.UNPINNED_MESSAGE: UnpinnedMessageEvent,
    EventTypes.UPDATED_PRIVATE_MESSAGE: UpdatePrivateMessageEvent,
    EventTypes.DELETED_PRIVATE_MESSAGE: DeletedPrivateMessageEvent,
    EventTypes.PRIVATE_ADDED_REACTION: PrivateAddedReactionEvent,
    EventTypes.PRIVATE_DELETED_REACTION: PrivateDeletedReactionEvent,
    EventTypes.JOINED_GUILD: JoinedGuildEvent,
    EventTypes.EXITED_GUILD: ExitedGuildEvent,
    EventTypes.UPDATED_GUILD_MEMBER: UpdatedGuildMemberEvent,
    EventTypes.GUILD_MEMBER_ONLINE: GuildMemberOnlineEvent,
    EventTypes.GUILD_MEMBER_OFFLINE: GuildMemberOfflineEvent,
    EventTypes.ADDED_ROLE: AddedRoleEvent,
    EventTypes.DELETED_ROLE: DeleteRoleEvent,
    EventTypes.UPDATED_ROLE: UpdateRoleEvent,
    EventTypes.UPDATED_GUILD: UpdateGuildEvent,
    EventTypes.DELETED_GUILD: DeleteGuildEvent,
    EventTypes.ADDED_BLOCK_LIST: AddedBlockListEvent,
    EventTypes.DELETED_BLOCK_LIST: DeleteBlockListEvent,
    EventTypes.ADDED_EMOJI: AddedEmojiEvent,
    EventTypes.DELETED_EMOJI: DeletedEmojiEvent,
    EventTypes.UPDATED_EMOJI: UpdateEmojiEvent,
    EventTypes.JOINED_CHANNEL: JoinedChannelEvent,
    EventTypes.EXITED_CHANNEL: ExitedChannelEvent,
    EventTypes.USER_UPDATED: UserUpdatedEvent,
    EventTypes.SELF_JOINED_GUILD: SelfJoinedGuildEvent,
    EventTypes.SELF_EXITED_GUILD: SelfExitedGuildEvent,
    EventTypes.MESSAGE_BTN_CLICK: MessageButtonClickEvent
}


class EventManager:
    """Register and post events"""

    def __call__(self, handle: EVENT_HANDLE_TYPE):
        self.subscribe(handle)

    def __init__(self):
        self._event_handles: Dict[Type[AbstractEvent], List[EVENT_HANDLE_TYPE]] = {}

    async def post(self, event: AbstractEvent):
        """post event to registered handles"""
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
    def make_event(event: Event) -> Optional[AbstractEvent]:
        """make event to typed event"""
        event_type = event.event_type

        cls = _EVENT_MAP.get(event_type, None)

        if cls:
            return cls(event.body)
        return None
