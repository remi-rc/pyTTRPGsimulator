import math
import copy
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING, Union
from .attributes import Attributes
from .modifiers import DamageModifier

if TYPE_CHECKING:
    from .entity import Entity


class Trait:
    def __init__(
        self,
        name="",
        duration: int = math.inf,
        damage_modifiers: Optional[List["DamageModifier"]] = None,
        attributes: "Attributes" = None,
        **kwargs,  # Check the Attributes class to know these additional arguments
    ):
        self.name = name
        self.duration = duration

        # Ensure damage_modifiers is always a list
        if isinstance(damage_modifiers, DamageModifier):
            self.damage_modifiers = [damage_modifiers]
        elif damage_modifiers is None:
            self.damage_modifiers = []
        elif isinstance(damage_modifiers, list):
            # Validate that all items in the list are of type DamageModifier
            if not all(
                isinstance(modifier, DamageModifier) for modifier in damage_modifiers
            ):
                raise TypeError(
                    "All items in the damage_modifiers list must be instances of DamageModifier"
                )
            self.damage_modifiers = damage_modifiers
        else:
            raise TypeError(
                "damage_modifiers must be either a DamageModifier or a list of DamageModifier"
            )

        # Update the attributes with any custom values provided via kwargs
        self.attributes = attributes if attributes is not None else Attributes()
        for key, value in kwargs.items():
            if hasattr(self.attributes, key):
                setattr(self.attributes, key, value)
            else:
                raise AttributeError(f"'Attributes' object has no attribute '{key}'")


@dataclass
class TraitsManager:
    traits: List["Trait"] = field(default_factory=list)

    # Reference to the entity that owns this traitManager
    entity: Optional["Entity"] = None

    def add_trait(self, new_trait: Union[Trait, List[Trait]]):
        if isinstance(new_trait, list):
            for trait in new_trait:
                self._add_single_trait(trait)
        else:
            self._add_single_trait(new_trait)

    def _add_single_trait(self, new_trait: Trait):
        for existing_trait in self.traits:
            if existing_trait.name == new_trait.name:
                # If the exact same trait is already in the list, update the duration
                existing_trait.duration = max(
                    existing_trait.duration, new_trait.duration
                )
                return

        # If the trait is not found, add it to the list
        self.traits.append(copy.deepcopy(new_trait))

    def remove_trait(self, traits: Union[Trait, List[Trait]]):
        [self.traits.remove(trait) for trait in traits]
        if isinstance(traits, list):
            # Extract trait names from the list of traits
            trait_names_to_remove = {trait.name for trait in traits}
            # Remove all traits with names in trait_names_to_remove
            self.traits = [
                t for t in self.traits if t.name not in trait_names_to_remove
            ]
        else:
            # Handle single trait case
            self.traits = [t for t in self.traits if t.name != traits.name]

    def update_traits(self):
        """
        Decrement the duration of each trait. If a trait expires (duration <= 0),
        remove it and invalidate the actor's attribute cache.
        """
        expired_traits = []
        for trait in self.traits:
            trait.duration -= 1
            if trait.duration <= 0:
                expired_traits.append(trait)

        # Remove expired traits and invalidate the actor's attributes
        for trait in expired_traits:
            self.remove_trait(trait)

        if expired_traits:
            if self.entity:
                self.entity.invalidate_cache()

    def get_active_traits(self) -> List["Trait"]:
        return self.traits

    def __str__(self):
        return f"traits: {', '.join([f'{trait.name} (Duration: {trait.duration})' for trait in self.traits])}"

    def __repr__(self):
        return self.__str__()
