import logging
from typing import List, Optional, Type, Dict, Union
from dataclasses import dataclass, fields
import math
import random

from .items import Item, Armor, Weapon, ItemManager
from .damages import Damage, Physical
from .modifiers import DamageModifier, ModifierManager, Resistance, Vulnerability
from .strategy import DefaultStrategy
from .attributes import Attributes, actor_attributes
from .traits import Trait, TraitsManager
from .entity import Entity

# Set up logging
logger = logging.getLogger(__name__)

logger.info("This is a test info message from module actors")
logger.error("This is a test error message from module actors")


class Actor(Entity):
    def __init__(
        self,
        name: str = "",
        items: Optional[List["Item"]] = None,
        traits: Optional[List["Trait"]] = None,
        attributes: "Attributes" = None,
        target_mode: str = "target_weakest",
        strategy=DefaultStrategy(),
        **kwargs,  # Check the Attributes class to know these additional arguments
    ):

        # Lazy evaluation cache
        self._cached_attributes = None
        self._cached_modifiers: Dict[Type[DamageModifier], List[DamageModifier]] = {}

        # Items management
        self.item_manager = ItemManager()
        self.item_manager.add_item(items if items is not None else [])

        # Combat-related properties
        self.strategy = strategy
        self.current_target: Optional["Actor"] = None
        self.targeting_enemies: List["Actor"] = []
        self.target_mode = target_mode
        self.attack_count = 0  # Track the number of attacks in the current turn
        self.advantage_count = 0  # Track the number of advantages gained
        self.one_time_hit_bonus = 0  # A bonus from help action
        self.help_count = 0  # number of times the actor has provided help this round
        self.is_dodging = False
        self.is_full_dodging = False
        self.position_X = 0
        self.position_Y = 0

        attributes = attributes if attributes is not None else actor_attributes
        super().__init__(name=name, traits=traits, attributes=attributes, **kwargs)

        # Set resources
        self.current_health_points = self.max_health_points
        self.current_stamina_points = self.max_stamina_points
        self.current_grit_points = self.max_grit_points
        self.current_mana_points = self.max_mana_points
        self.current_action_points = self.max_action_points

    def reset_attack_count(self):
        self.attack_count = 0

    def reset_advantage_count(self):
        self.advantage_count = 0

    def update_targeting(self, team_allies: List["Actor"], team_enemies: List["Actor"]):
        """
        Update the current target of the actor based on the given allies and enemies.
        """
        # Check if current target is dead
        if self.current_target and self.current_target.current_health_points <= 0:
            self.current_target = None

        # Remove target if allied actor (because of Help, Heal, Mind Control, etc)
        if self.current_target in team_allies:
            self.current_target = None

        # Filter out dead enemies
        alive_enemies = [
            enemy for enemy in team_enemies if enemy.current_health_points > 0
        ]

        # Determine enemies targeting this actor
        enemies_targeting_me = [
            enemy for enemy in self.targeting_enemies if enemy.current_target == self
        ]

        # Determine the weakest ally who is still alive
        alive_allies = [ally for ally in team_allies if ally.current_health_points > 0]
        weakest_ally = min(
            alive_allies, key=lambda ally: ally.current_health_points, default=None
        )

        if enemies_targeting_me:
            # If there are enemies targeting this actor, select among them based on target_mode
            self.current_target = self.select_target(enemies_targeting_me)
        elif (
            self.target_mode == "help_ally"
            and weakest_ally
            and weakest_ally.current_target
            and weakest_ally.current_target.current_health_points > 0
        ):
            # If help ally mode, target the same enemy as the weakest ally
            self.current_target = weakest_ally.current_target
        else:
            # Select freely among all alive enemies
            self.current_target = self.select_target(alive_enemies)

        if self.current_target:
            logger.info(f"{self.name} is now targeting {self.current_target.name}")

    def select_target(self, candidates: List["Actor"]) -> Optional["Actor"]:
        """
        Select a target from the given candidates based on the target mode.

        TODO: should target mode be a class ?
        """
        if not candidates:
            return None
        if self.target_mode == "target_weakest":
            return min(candidates, key=lambda enemy: enemy.health_points)
        elif self.target_mode == "target_strongest":
            return max(candidates, key=lambda enemy: enemy.health_points)
        elif self.target_mode == "random":
            n = random.randint(0, len(candidates) - 1)
            return candidates[n]
        else:
            # Default to targeting the weakest
            return min(candidates, key=lambda enemy: enemy.health_points)

    def roll_initiative(self):
        roll = random.randint(1, 20)
        bonus = self.attributes.initiative
        if bonus != 0:
            logger.info(f"{self.name} gets {roll + bonus} ({roll} + {bonus})")
        else:
            logger.info(f"{self.name} gets {roll}")

        return roll + bonus

    def calculate_damage_taken(self, damage: "Damage") -> float:
        """
        Calculate the total damage taken by the actor after applying resistances,
        vulnerabilities, and armor reductions.

        Parameters:
            damage (Damage): The damage object containing the value and type of damage.

        Returns:
            float: The final damage value after all modifications.
        """
        # Initial damage value
        damage_value = damage.value

        # Directly use the type of the damage type
        damage_type = type(damage.damage_type)

        # Gather all resistances and vulnerabilities of the same damage type
        resistances = [
            res for res in self.resistances if isinstance(res.damage_type, damage_type)
        ]
        vulnerabilities = [
            vul
            for vul in self.vulnerabilities
            if isinstance(vul.damage_type, damage_type)
        ]

        # Apply additive and multiplicative resistances
        additive_resistance = sum(
            res.value for res in resistances if not res.is_multiplicative
        )
        multiplicative_resistance = 1
        for res in resistances:
            if res.is_multiplicative:
                multiplicative_resistance *= res.value

        damage_value = (damage_value - additive_resistance) * multiplicative_resistance

        # Apply additive and multiplicative vulnerabilities
        additive_vulnerability = sum(
            vul.value for vul in vulnerabilities if not vul.is_multiplicative
        )
        multiplicative_vulnerability = 1
        for vul in vulnerabilities:
            if vul.is_multiplicative:
                multiplicative_vulnerability *= vul.value

        damage_value = (
            damage_value + additive_vulnerability
        ) * multiplicative_vulnerability

        # Apply armor reduction based on damage type
        reduction = (
            self.attributes.mystical_damage_reduction
            if not isinstance(damage.damage_type, Physical)
            else self.attributes.physical_damage_reduction
        )
        damage_value -= reduction

        # Ensure the damage value is not negative
        damage_value = max(damage_value, 0)

        return damage_value

    def take_damage(self, damages: List["Damage"]):
        """
        Apply a list of damages to the actor, updating health points accordingly.
        """
        total_damage = 0
        for damage in damages:
            total_damage += self.calculate_damage_taken(damage)
        self.current_health_points -= total_damage
        logger.info(
            f"* {self.name} took {total_damage} {damage.damage_type} damage and has {self.current_health_points} HP left."
        )

    def add_item(self, item: Union[Item, List[Item]]):
        if isinstance(item, list):
            self.item_manager.add_item(item)
        else:
            self.item_manager.add_item([item])
        self.invalidate_cache()

    def remove_item(self, item: Union[Item, List[Item]]):
        if isinstance(item, list):
            self.item_manager.remove_item(item)
        else:
            self.item_manager.remove_item([item])
        self.invalidate_cache()

    def get_attribute_sources(self):
        """
        Returns a list of all sources of attributes for this actor.
        Includes base attributes, traits, and items.
        """
        # Start with the base attributes and traits (defined by Entity)
        sources = super().get_attribute_sources()

        # Add attributes from items
        sources += [item.attributes for item in self.item_manager.get_items()]

        return sources

    def get_modifier_sources(self) -> List[Union["Trait"]]:
        """
        Returns a list of all sources of modifiers for this actor.
        Includes traits and items.
        """
        # Start with the trait sources
        sources = (
            self.traits_manager.get_active_traits()
        )  # super().get_modifier_sources()
        print("sources =", [source.name for source in sources])

        # Add items as sources of modifiers
        # for item in self.item_manager.get_items():
        #     if item.traits:  # Check if the item has traits and they are not None
        #         sources += item.traits

        return sources

    def new_round(self):
        self.traits_manager.update_traits()
        self.current_action_points = self.max_action_points
        self.reset_attack_count()
        self.reset_advantage_count()
        self.help_count = 0

    @property
    def prime_modifier(self) -> int:
        """
        Return the highest attribute value among Might, Agility, Intelligence, and Charisma.
        """
        return (
            max([self.might, self.agility, self.intelligence, self.charisma])
            + self.prime_modifier_bonus
        )

    @property
    def weapons(self) -> List["Weapon"]:
        return self.item_manager.get_items_of_type(Weapon)

    @property
    def armors(self) -> List["Armor"]:
        return self.item_manager.get_items_of_type(Armor)

    @property
    def is_alive(self) -> bool:
        return self.current_health_points > 0

    @property
    def is_at_death_door(self) -> bool:
        return (self.current_health_points < 0) & (
            self.current_health_points > self.attributes.death_threshold
        )

    def full_rest(self):
        """
        Restore all attributes to their maximum values, simulating a full rest.
        """
        self.current_health_points = self.max_health_points
        self.current_stamina_points = self.max_stamina_points
        self.current_grit_points = self.max_grit_points
        self.current_mana_points = self.max_mana_points
        self.current_action_points = self.max_action_points
        self.reset_attack_count()
        self.reset_advantage_count()
        self.help_count = 0
        logger.info(f"{self.name} has fully rested and all attributes are restored.")
