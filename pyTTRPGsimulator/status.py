import math
import copy
from dataclasses import dataclass, field
from typing import List, Optional, Type, TYPE_CHECKING
from .attributes import Attributes
from .modifiers import DamageModifier

if TYPE_CHECKING:
    from .actors import Actor


class StatusEffect:
    def __init__(
        self,
        name="",
        duration: int = math.inf,
        damage_modifiers: Optional[List["DamageModifier"]] = None,
        **kwargs,  # Check the Attributes class to know these additional arguments
    ):
        self.name = name
        self.duration = duration
        self.damage_modifiers = damage_modifiers if damage_modifiers is not None else []
        self.base_attributes = Attributes()

        # Update the attributes with any custom values provided via kwargs
        for key, value in kwargs.items():
            if hasattr(self.base_attributes, key):
                setattr(self.base_attributes, key, value)
            else:
                raise AttributeError(f"'Attributes' object has no attribute '{key}'")


@dataclass
class StatusManager:
    statuses: List["StatusEffect"] = field(default_factory=list)

    # Reference to the actor that owns this StatusManager
    entity: Optional["Actor"] = None

    # TODO : generalize to all entities ?

    def add_status(self, new_status: StatusEffect):
        for _, status in enumerate(self.statuses):
            if status.name == new_status.name:
                # If the exact same Python object is already in the list, update the duration
                status.duration = max(status.duration, new_status.duration)
                return

        # If the status is not found, add it to the list
        self.statuses.append(copy.deepcopy(new_status))

    def remove_status(self, status: StatusEffect):
        if status in self.statuses:
            self.statuses.remove(status)

    def update_statuses(self):
        """
        Decrement the duration of each status. If a status expires (duration <= 0),
        remove it and invalidate the actor's attribute cache.
        """
        expired_statuses = []
        for status in self.statuses:
            status.duration -= 1
            if status.duration <= 0:
                expired_statuses.append(status)

        # Remove expired statuses and invalidate the actor's attributes
        for status in expired_statuses:
            self.remove_status(status)

        if expired_statuses:
            if self.entity:
                self.entity.invalidate_cache()

    def get_active_statuses(self) -> List["StatusEffect"]:
        return self.statuses

    def __str__(self):
        return f"Statuses: {', '.join([f'{status.name} (Duration: {status.duration})' for status in self.statuses])}"

    def __repr__(self):
        return self.__str__()
