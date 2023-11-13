from .event import AbstractEvent
from ... import Role


class AbstractRoleEvent(AbstractEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.role = Role(**raw)


class AddedRoleEvent(AbstractRoleEvent):
    pass


class DeleteRoleEvent(AbstractRoleEvent):
    pass


class UpdateRoleEvent(AbstractRoleEvent):
    pass
