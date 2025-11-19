"""
Living NPC Entity

NPCs with behaviors, state, and AI.
"""

from typing import Optional, Dict, Any, List
import random
from .base_entity import BaseEntity


class LivingNPC(BaseEntity):
    """
    NPC with dynamic behaviors and state.

    Wraps generated NPC data and adds simulation capabilities:
    - Movement between locations
    - Daily routines (work, eat, sleep)
    - Social interactions
    - Inventory management
    - Energy/mood systems
    - Goal-driven behavior
    """

    # Activity types
    IDLE = "idle"
    WORKING = "working"
    TRAVELING = "traveling"
    EATING = "eating"
    SLEEPING = "sleeping"
    SOCIALIZING = "socializing"
    SHOPPING = "shopping"

    def __init__(self, entity_id: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None,
                 world_context: Any = None):
        """
        Initialize living NPC.

        Args:
            entity_id: Unique ID
            data: Generated NPC data from GenerationEngine
            world_context: Reference to world
        """
        super().__init__(entity_id, data)
        self.world = world_context

        # Simulation state (not in generated data)
        self.current_location_id = data.get("location") if data else None
        self.current_activity = self.IDLE
        self.destination_location_id = None
        self.travel_progress = 0.0  # 0.0 to 1.0

        # Needs & State
        self.energy = 100.0  # 0-100
        self.hunger = 0.0  # 0-100 (higher = more hungry)
        self.mood = 50.0  # 0-100 (higher = happier)
        self.gold = data.get("gold", random.randint(10, 500)) if data else 100

        # Goals & memory
        self.current_goal = None
        self.goal_queue = []
        self.memory = []  # Recent events
        self.max_memory = 20

        # Social
        self.conversation_partner = None
        self.last_conversation_time = 0

        # Work schedule (hours of day)
        self.work_start_hour = 8
        self.work_end_hour = 17
        self.work_location_id = self.current_location_id  # Where they work

    def update(self, delta_time: float, world_context: Any):
        """
        Update NPC state each simulation tick.

        Args:
            delta_time: Minutes elapsed since last update
            world_context: Reference to world
        """
        if not self.active:
            return

        self.world = world_context
        self.last_update += delta_time

        # Update needs
        self._update_needs(delta_time)

        # Check if we need to handle urgent needs
        if self._handle_urgent_needs():
            return  # Urgent need takes priority

        # Handle current activity
        if self.current_activity == self.TRAVELING:
            self._update_travel(delta_time)
        elif self.current_activity == self.WORKING:
            self._update_work(delta_time)
        elif self.current_activity == self.EATING:
            self._update_eating(delta_time)
        elif self.current_activity == self.SLEEPING:
            self._update_sleeping(delta_time)
        elif self.current_activity == self.SOCIALIZING:
            self._update_socializing(delta_time)
        else:
            # Idle - decide what to do based on profession and time
            self._decide_activity()

    def _update_needs(self, delta_time: float):
        """Update energy, hunger, mood based on time passing"""
        # Energy decreases over time, faster when working
        if self.current_activity == self.WORKING:
            self.energy -= delta_time * 0.15
        elif self.current_activity == self.SLEEPING:
            self.energy += delta_time * 0.5
        else:
            self.energy -= delta_time * 0.05

        # Hunger increases over time
        self.hunger += delta_time * 0.1

        # Eating reduces hunger, increases energy slightly
        if self.current_activity == self.EATING:
            self.hunger -= delta_time * 1.0
            self.energy += delta_time * 0.2

        # Clamp values
        self.energy = max(0, min(100, self.energy))
        self.hunger = max(0, min(100, self.hunger))

        # Mood affected by energy and hunger
        if self.energy < 30 or self.hunger > 70:
            self.mood -= delta_time * 0.1
        else:
            self.mood += delta_time * 0.05

        self.mood = max(0, min(100, self.mood))

    def _handle_urgent_needs(self) -> bool:
        """
        Handle urgent needs (sleep, food).

        Returns:
            True if handling urgent need, False otherwise
        """
        # Critical sleep need
        if self.energy < 20 and self.current_activity != self.SLEEPING:
            self.start_sleeping()
            return True

        # Critical hunger
        if self.hunger > 80 and self.current_activity != self.EATING:
            self.start_eating()
            return True

        return False

    def _decide_activity(self):
        """Decide what to do based on time, profession, and state"""
        if not self.world:
            return

        time_manager = self.world.time_manager

        # Sleep at night
        if not time_manager.is_daytime and self.energy < 60:
            self.start_sleeping()
            return

        # Work during working hours
        if time_manager.is_working_hours:
            if self._should_work():
                self.start_working()
                return

        # Eat if moderately hungry
        if self.hunger > 50:
            self.start_eating()
            return

        # Socialize occasionally
        if random.random() < 0.1:
            self.start_socializing()
            return

        # Default: idle
        self.current_activity = self.IDLE

    def _should_work(self) -> bool:
        """Determine if NPC should work based on profession"""
        if not self.data or "professions" not in self.data:
            return False

        professions = self.data["professions"]
        work_professions = ["blacksmith", "merchant", "guard", "innkeeper",
                           "alchemist", "enchanter", "farmer", "miner"]

        return any(prof in work_professions for prof in professions)

    def start_working(self):
        """Begin working"""
        self.current_activity = self.WORKING
        if self.world:
            self.world.event_system.publish_event(
                "npc_started_working",
                source_id=self.id,
                location_id=self.current_location_id,
                data={"npc_name": self.data.get("name", "Unknown")}
            )

    def _update_work(self, delta_time: float):
        """Update working activity"""
        # Work until end of work hours or too tired
        if self.world and not self.world.time_manager.is_working_hours:
            self.current_activity = self.IDLE
        elif self.energy < 30:
            self.current_activity = self.IDLE

        # Profession-specific work outcomes
        if self._can_craft():
            self._maybe_craft_item(delta_time)

    def _can_craft(self) -> bool:
        """Check if NPC can craft items"""
        if not self.data:
            return False
        professions = self.data.get("professions", [])
        crafting_professions = ["blacksmith", "alchemist", "enchanter", "jeweler"]
        return any(prof in crafting_professions for prof in professions)

    def _maybe_craft_item(self, delta_time: float):
        """Randomly craft items while working"""
        # Small chance per minute of crafting
        if random.random() < (delta_time * 0.01):  # ~1% per minute
            if self.world and self.world.generator_adapter:
                # Determine what to craft based on profession
                template = self._get_craft_template()
                if template:
                    item = self.world.generator_adapter.spawn_item(template)
                    self.data.setdefault("inventory", []).append(item)

                    self.world.event_system.publish_event(
                        "item_crafted",
                        source_id=self.id,
                        location_id=self.current_location_id,
                        data={"item": item, "crafter": self.data.get("name")}
                    )

    def _get_craft_template(self) -> Optional[str]:
        """Get item template based on profession"""
        if not self.data:
            return None

        professions = self.data.get("professions", [])

        if "blacksmith" in professions:
            return random.choice(["weapon_melee", "armor"])
        elif "alchemist" in professions:
            return "consumable"
        elif "enchanter" in professions:
            return random.choice(["scroll", "jewelry"])

        return None

    def start_eating(self):
        """Begin eating"""
        self.current_activity = self.EATING
        # Will finish eating after ~15 minutes

    def _update_eating(self, delta_time: float):
        """Update eating activity"""
        # Finish eating when hunger is low
        if self.hunger < 20:
            self.current_activity = self.IDLE

    def start_sleeping(self):
        """Begin sleeping"""
        self.current_activity = self.SLEEPING

    def _update_sleeping(self, delta_time: float):
        """Update sleeping activity"""
        # Wake up when rested or it's daytime
        if self.energy > 90:
            self.current_activity = self.IDLE
        elif self.world and self.world.time_manager.is_working_hours:
            if self.energy > 50:
                self.current_activity = self.IDLE

    def start_socializing(self):
        """Begin socializing"""
        self.current_activity = self.SOCIALIZING
        # Socializing improves mood
        self.mood += 5

    def _update_socializing(self, delta_time: float):
        """Update socializing activity"""
        # Socialize for a while then return to idle
        if delta_time > 10:  # Socialize for ~10 minutes
            self.current_activity = self.IDLE

    def move_to_location(self, location_id: str):
        """
        Start moving to a new location.

        Args:
            location_id: Target location ID
        """
        if location_id == self.current_location_id:
            return

        self.current_activity = self.TRAVELING
        self.destination_location_id = location_id
        self.travel_progress = 0.0

        if self.world:
            self.world.event_system.publish_event(
                "npc_started_traveling",
                source_id=self.id,
                location_id=self.current_location_id,
                data={
                    "npc_name": self.data.get("name"),
                    "destination": location_id
                }
            )

    def _update_travel(self, delta_time: float):
        """Update travel progress"""
        # Travel at ~1 location per hour (60 minutes)
        travel_speed = 1.0 / 60.0  # Progress per minute
        self.travel_progress += delta_time * travel_speed

        if self.travel_progress >= 1.0:
            # Arrived!
            old_location = self.current_location_id
            self.current_location_id = self.destination_location_id
            self.destination_location_id = None
            self.travel_progress = 0.0
            self.current_activity = self.IDLE

            if self.world:
                self.world.event_system.publish_event(
                    "npc_arrived",
                    source_id=self.id,
                    location_id=self.current_location_id,
                    data={
                        "npc_name": self.data.get("name"),
                        "from_location": old_location
                    }
                )

    def add_memory(self, event: str):
        """
        Add event to NPC's memory.

        Args:
            event: Event description
        """
        self.memory.append(event)
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)

    def get_name(self) -> str:
        """Get NPC name"""
        return self.data.get("name", "Unknown") if self.data else "Unknown"

    def get_profession(self) -> str:
        """Get primary profession"""
        if self.data and "professions" in self.data:
            professions = self.data["professions"]
            return professions[0] if professions else "wanderer"
        return "wanderer"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize NPC to dictionary"""
        return {
            "id": self.id,
            "data": self.data,
            "current_location_id": self.current_location_id,
            "current_activity": self.current_activity,
            "destination_location_id": self.destination_location_id,
            "travel_progress": self.travel_progress,
            "energy": self.energy,
            "hunger": self.hunger,
            "mood": self.mood,
            "gold": self.gold,
            "memory": self.memory,
            "work_start_hour": self.work_start_hour,
            "work_end_hour": self.work_end_hour,
            "work_location_id": self.work_location_id,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], world_context: Any) -> 'LivingNPC':
        """Deserialize NPC from dictionary"""
        npc = cls(
            entity_id=data["id"],
            data=data["data"],
            world_context=world_context
        )

        npc.current_location_id = data.get("current_location_id")
        npc.current_activity = data.get("current_activity", cls.IDLE)
        npc.destination_location_id = data.get("destination_location_id")
        npc.travel_progress = data.get("travel_progress", 0.0)
        npc.energy = data.get("energy", 100.0)
        npc.hunger = data.get("hunger", 0.0)
        npc.mood = data.get("mood", 50.0)
        npc.gold = data.get("gold", 100)
        npc.memory = data.get("memory", [])
        npc.work_start_hour = data.get("work_start_hour", 8)
        npc.work_end_hour = data.get("work_end_hour", 17)
        npc.work_location_id = data.get("work_location_id")
        npc.active = data.get("active", True)

        return npc
