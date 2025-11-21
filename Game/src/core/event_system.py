"""
Event System for World Simulation

Pub/sub event bus for entity interactions and world events.
"""

from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from datetime import datetime
import uuid


class Event:
    """Represents a single event in the simulation"""

    def __init__(self, event_type: str, data: Optional[Dict[str, Any]] = None,
                 source_id: Optional[str] = None, target_id: Optional[str] = None,
                 location_id: Optional[str] = None):
        """
        Initialize an event.

        Args:
            event_type: Type of event (e.g., "npc_moved", "item_crafted", "quest_completed")
            data: Additional event data
            source_id: ID of entity that triggered the event
            target_id: ID of entity affected by the event
            location_id: ID of location where event occurred
        """
        self.id = str(uuid.uuid4())
        self.event_type = event_type
        self.data = data or {}
        self.source_id = source_id
        self.target_id = target_id
        self.location_id = location_id
        self.timestamp = None  # Set by EventSystem when processed

    def __repr__(self):
        return f"Event({self.event_type}, source={self.source_id}, target={self.target_id})"


class EventSystem:
    """
    Event bus for managing simulation events.

    Supports:
    - Event publishing and subscription
    - Event queuing and processing
    - Event history tracking
    - Conditional event triggers
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize the event system.

        Args:
            max_history: Maximum number of events to keep in history
        """
        # Subscribers: {event_type: [callbacks]}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

        # Event queue (events waiting to be processed)
        self.event_queue: List[Event] = []

        # Event history (processed events)
        self.event_history: List[Event] = []
        self.max_history = max_history

        # Global event listeners (called for all events)
        self.global_listeners: List[Callable] = []

    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to events of a specific type.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs (receives Event object)
        """
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Unsubscribe from events.

        Args:
            event_type: Type of event
            callback: Callback to remove
        """
        if event_type in self.subscribers:
            if callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)

    def add_global_listener(self, callback: Callable):
        """
        Add a listener that receives all events.

        Args:
            callback: Function to call for every event
        """
        self.global_listeners.append(callback)

    def publish(self, event: Event, immediate: bool = False):
        """
        Publish an event.

        Args:
            event: Event to publish
            immediate: If True, process immediately; otherwise queue for later
        """
        if immediate:
            self._process_event(event)
        else:
            self.event_queue.append(event)

    def publish_event(self, event_type: str, data: Optional[Dict[str, Any]] = None,
                     source_id: Optional[str] = None, target_id: Optional[str] = None,
                     location_id: Optional[str] = None, immediate: bool = False):
        """
        Convenience method to create and publish an event.

        Args:
            event_type: Type of event
            data: Event data
            source_id: Source entity ID
            target_id: Target entity ID
            location_id: Location ID
            immediate: Process immediately or queue
        """
        event = Event(event_type, data, source_id, target_id, location_id)
        self.publish(event, immediate=immediate)

    def process_events(self, max_events: Optional[int] = None):
        """
        Process queued events.

        Args:
            max_events: Maximum number of events to process (None = all)
        """
        events_to_process = self.event_queue[:max_events] if max_events else self.event_queue
        self.event_queue = self.event_queue[len(events_to_process):]

        for event in events_to_process:
            self._process_event(event)

    def _process_event(self, event: Event):
        """
        Process a single event by calling all subscribers.

        Args:
            event: Event to process
        """
        # Set timestamp
        event.timestamp = datetime.now()

        # Call global listeners
        for listener in self.global_listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"Error in global listener: {e}")

        # Call type-specific subscribers
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error processing event {event.event_type}: {e}")

        # Add to history
        self.event_history.append(event)

        # Trim history if needed
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

    def get_events_by_type(self, event_type: str, limit: Optional[int] = None) -> List[Event]:
        """
        Get events from history by type.

        Args:
            event_type: Type of events to retrieve
            limit: Maximum number of events to return (most recent first)

        Returns:
            List of matching events
        """
        matching = [e for e in reversed(self.event_history) if e.event_type == event_type]
        return matching[:limit] if limit else matching

    def get_events_by_source(self, source_id: str, limit: Optional[int] = None) -> List[Event]:
        """Get events from history by source entity"""
        matching = [e for e in reversed(self.event_history) if e.source_id == source_id]
        return matching[:limit] if limit else matching

    def get_events_by_location(self, location_id: str, limit: Optional[int] = None) -> List[Event]:
        """Get events from history by location"""
        matching = [e for e in reversed(self.event_history) if e.location_id == location_id]
        return matching[:limit] if limit else matching

    def get_recent_events(self, limit: int = 10) -> List[Event]:
        """Get most recent events"""
        return list(reversed(self.event_history[-limit:]))

    def clear_history(self):
        """Clear event history"""
        self.event_history.clear()

    def clear_queue(self):
        """Clear event queue"""
        self.event_queue.clear()

    def get_queue_size(self) -> int:
        """Get number of queued events"""
        return len(self.event_queue)

    def to_dict(self) -> dict:
        """Serialize to dictionary (excluding callbacks)"""
        return {
            "queue_size": len(self.event_queue),
            "history_size": len(self.event_history),
            "max_history": self.max_history,
            "recent_events": [
                {
                    "type": e.event_type,
                    "source": e.source_id,
                    "target": e.target_id,
                    "location": e.location_id,
                    "data": e.data,
                }
                for e in self.get_recent_events(20)
            ]
        }


# Common event types
class EventTypes:
    """Standard event type constants"""

    # Entity events
    ENTITY_SPAWNED = "entity_spawned"
    ENTITY_DESTROYED = "entity_destroyed"
    ENTITY_MOVED = "entity_moved"

    # NPC events
    NPC_SPAWNED = "npc_spawned"
    NPC_DIED = "npc_died"
    NPC_MOVED = "npc_moved"
    NPC_CONVERSATION = "npc_conversation"
    NPC_TRADED = "npc_traded"
    NPC_RELATIONSHIP_CHANGED = "npc_relationship_changed"

    # Item events
    ITEM_CREATED = "item_created"
    ITEM_DESTROYED = "item_destroyed"
    ITEM_TRADED = "item_traded"
    ITEM_EQUIPPED = "item_equipped"
    ITEM_DROPPED = "item_dropped"

    # Location events
    LOCATION_CREATED = "location_created"
    LOCATION_ENTERED = "location_entered"
    LOCATION_EXITED = "location_exited"

    # Quest events
    QUEST_STARTED = "quest_started"
    QUEST_COMPLETED = "quest_completed"
    QUEST_FAILED = "quest_failed"

    # Economy events
    MARKET_OPENED = "market_opened"
    MARKET_CLOSED = "market_closed"
    PRICE_CHANGED = "price_changed"
    TRADE_COMPLETED = "trade_completed"

    # Combat events
    COMBAT_STARTED = "combat_started"
    COMBAT_ENDED = "combat_ended"
    DAMAGE_DEALT = "damage_dealt"

    # Weather events
    WEATHER_CHANGED = "weather_changed"
    SEASON_CHANGED = "season_changed"

    # Time events
    HOUR_PASSED = "hour_passed"
    DAY_PASSED = "day_passed"
    YEAR_PASSED = "year_passed"
