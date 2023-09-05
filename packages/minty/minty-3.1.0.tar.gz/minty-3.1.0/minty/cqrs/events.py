# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import datetime
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Self, TypedDict
from uuid import UUID, uuid4

from .. import Base

if TYPE_CHECKING:
    from . import UserInfo


class EntityChange(TypedDict):
    key: str
    old_value: Any
    new_value: Any


def event(name: str, extra_fields: list[str] | None = None):
    """Decorator to capture entity changes and publish events to the event_service.

    :param name: Name of event to publish
    :type name: str
    :param extra_fields: extra fields to capture publish with event, defaults to None
    :type extra_fields: List, optional
    :return: wrapped_entity
    :rtype: func
    """

    def register_event(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            wrapped_entity = args[0]

            if extra_fields is not None:
                wrapped_entity.capture_field_values(fields=extra_fields)

            wrapped_entity.event_service.log_event(
                entity_type=wrapped_entity.__class__.__name__,
                entity_id=wrapped_entity.entity_id,
                event_name=name,
                changes=wrapped_entity.change_log,
                entity_data=wrapped_entity.entity_data,
            )

            wrapped_entity.clear_entity_data()
            wrapped_entity.clear_change_log()

        return wrapper

    return register_event


@dataclass
class Event:
    uuid: UUID
    created_date: datetime.datetime

    correlation_id: UUID
    domain: str
    context: str
    user_uuid: UUID

    entity_type: str
    # Moving to "fully UUID" requires some careful versioning and planning, as
    # dependent code may need to be adjusted.
    entity_id: str | UUID

    event_name: str
    changes: list[EntityChange]
    entity_data: dict
    processed: bool = False
    user_info: Optional["UserInfo"] = None

    @classmethod
    def create_basic(
        cls,
        domain: str,
        context: str,
        entity_type: str,
        entity_id: UUID,
        event_name: str,
        entity_data: dict[str, Any],
        user_info: "UserInfo",
    ) -> Self:
        return cls(
            uuid=uuid4(),
            created_date=datetime.datetime.now(tz=datetime.UTC),
            correlation_id=uuid4(),
            domain=domain,
            context=context,
            entity_type=entity_type,
            entity_id=entity_id,
            event_name=event_name,
            changes=[],
            entity_data=entity_data,
            user_uuid=user_info.user_uuid,
            user_info=user_info,
        )

    def as_json(self) -> str:
        user_uuid = str(
            self.user_info.user_uuid if self.user_info else self.user_uuid
        )

        return json.dumps(
            {
                "id": str(self.uuid),
                "created_date": self.created_date.isoformat(),
                "correlation_id": str(self.correlation_id),
                "context": self.context,
                "domain": self.domain,
                "user_uuid": user_uuid,
                "user_info": json.loads(self.user_info.json())
                if self.user_info
                else None,
                "entity_type": self.entity_type,
                "entity_id": str(self.entity_id),
                "event_name": self.event_name,
                "changes": self.changes,
                "entity_data": self.entity_data,
            },
            sort_keys=True,
        )

    def routing_key(self) -> str:
        formatted_domain = str(self.domain).replace(".", "_")
        return ".".join(
            [
                "zsnl",
                "v2",
                formatted_domain,
                self.entity_type,
                self.event_name,
            ]
        )

    def format_changes(self) -> dict:
        """Format changes into more workable format.

        :return: dict with changes
        :rtype: dict
        """
        changes = {}
        for change in self.changes:
            changes[change["key"]] = change["new_value"]
        return changes

    def previous_value(self, key):
        """Returns the "old value" from the changelog for the given attribute

        :return: value containing the old value
        :rtype: str
        """
        values = [
            change["old_value"]
            for change in self.changes
            if change["key"] == key
        ]
        return values[0]

    def new_value(self, key):
        """Returns the "new value" from the changelog for the given attribute

        :return: value containing the old value
        :rtype: str
        """
        values = [
            change["new_value"]
            for change in self.changes
            if change["key"] == key
        ]
        return values[0]


class EventService(Base):
    __slots__ = (
        "event_list",
        "correlation_id",
        "domain",
        "context",
        "user_uuid",
        "user_info",
    )

    def __init__(
        self,
        correlation_id: UUID,
        domain: str,
        context: str,
        user_uuid: UUID,
        user_info: Optional["UserInfo"] = None,
    ):
        self.correlation_id = correlation_id
        self.domain = domain
        self.context = context

        self.user_info: UserInfo | None

        # If user_info is specified, it gets priority
        if user_info:
            self.user_info = user_info
            self.user_uuid = user_info.user_uuid
        else:
            self.user_info = None
            self.user_uuid = user_uuid

        self.event_list: list[Event] = []

    def log_event(
        self,
        entity_type: str,
        entity_id: str | UUID,
        event_name: str,
        changes: list[EntityChange],
        entity_data: dict[str, Any],
    ):
        """Register a new event with the event serivce

        This will create a new event using the `EventFactory` configured on
        initialization and append it to the `event_list`.

        :param event_name: Name of the event that happened
        :type event_name: str
        :param parameters: Dictionary containing the event parameters (like
            entity state pre-event and post-event)
        :type parameters: dict
        """

        uuid = uuid4()
        created_date = datetime.datetime.now(tz=datetime.UTC)

        event = Event(
            uuid=uuid,
            created_date=created_date,
            correlation_id=self.correlation_id,
            domain=self.domain,
            context=self.context,
            user_uuid=self.user_uuid,
            user_info=self.user_info,
            entity_type=entity_type,
            entity_id=entity_id,
            event_name=event_name,
            changes=changes,
            entity_data=entity_data,
        )

        self.logger.info(f"Created Event: {event}")

        self.event_list.append(event)

    def get_events_by_type(self, entity_type: str) -> list[Event]:
        """Get all events for given `entity_type`.

        :param entity_type: entity_type
        :type entity_type: str
        :return: list of events
        :rtype: typing.List[Event]
        """
        events = [
            ev for ev in self.event_list if ev.entity_type == entity_type
        ]
        return events
