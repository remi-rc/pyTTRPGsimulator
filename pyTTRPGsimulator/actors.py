import logging
from typing import List, Optional, Type, Dict, Union
import random
import math
import copy

from .items import Item, Armor, Weapon, ItemManager
from .damages import Damage, Physical
from .modifiers import DamageModifier
from .combat_strategies import DefaultStrategy
from .targeting_strategies import TargetWeakestStrategy
from .attributes import Attributes, actor_attributes
from .traits import Trait
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
        traits: Optional[Union["Trait", List["Trait"]]] = None,
        attributes: "Attributes" = None,
        targeting_strategy=TargetWeakestStrategy(),
        combat_strategy=DefaultStrategy(),
        **kwargs,  # Check the Attributes class to know these additional arguments
    ):

        # Lazy evaluation cache
        self._cached_attributes = None
        self._cached_modifiers: Dict[Type[DamageModifier], List[DamageModifier]] = {}

        # Items management
        self.item_manager = ItemManager()
        self.item_manager.add_item(items if items is not None else [])

        # Combat-related properties
        self.combat_strategy = combat_strategy
        self.current_target: Optional["Actor"] = None
        # TODO : Not sure how to best implement the targeting enemies dynamically
        self.targeting_enemies: List["Actor"] = []
        self.targeting_strategy = targeting_strategy
        self.attack_count = 0  # Track the number of attacks in the current turn
        self.advantage_count = 0  # Track the number of advantages gained
        self.one_time_hit_bonus = 0  # A bonus from help action
        self.help_count = 0  # number of times the actor has provided help this round
        self.is_dodging = False
        self.is_full_dodging = False
        self.position_X = 0
        self.position_Y = 0

        #  DANGER : A deepcopy is required to avoid sharing attributes among actors
        attributes = (
            attributes if attributes is not None else copy.deepcopy(actor_attributes)
        )
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
        self.targeting_strategy.select_target(self, team_allies, team_enemies)

    def roll_initiative(self):
        roll = random.randint(1, 20) + self.get_bonus_roll()
        bonus = self.attributes.initiative
        if bonus != 0:
            logger.info(f"{self.name} gets {roll + bonus} ({roll} + {bonus})")
        else:
            logger.info(f"{self.name} gets {roll}")

        return roll + bonus

    def roll_save(self, characteristic):
        roll = random.randint(1, 20) + self.get_bonus_roll()

        if characteristic.upper() == "MIGHT":
            bonus = self.might
        elif characteristic.upper() == "AGILITY":
            bonus = self.agility
        elif characteristic.upper() == "INTELLIGENCE":
            bonus = self.intelligence
        elif characteristic.upper() == "CHARISMA":
            bonus = self.charisma

        return roll + bonus

    def get_bonus_roll(self):
        return (
            self.D8_roll_bonus * random.randint(1, 8)
            + self.D6_roll_bonus * random.randint(1, 6)
            + self.D4_roll_bonus * random.randint(1, 4)
        )

    def calculate_damage_taken(
        self, damage: "Damage", ignore_damage_reduction=False
    ) -> float:
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

        # Apply armor reduction based on damage type (except if ignore_damage_reduction=True)
        if not ignore_damage_reduction:
            reduction = (
                self.attributes.mystical_damage_reduction
                if not isinstance(damage.damage_type, Physical)
                else self.attributes.physical_damage_reduction
            )
            damage_value -= reduction

        # Ensure the damage value is not negative
        damage_value = max(damage_value, 0)

        return damage_value

    def take_damage(self, damages: List["Damage"], ignore_damage_reduction=False):
        """
        Apply a list of damages to the actor, updating health points accordingly.
        Log each type of damage separately in a detailed and structured way.
        """
        total_damage = 0
        damage_report = []

        for damage in damages:
            calculated_damage = self.calculate_damage_taken(
                damage, ignore_damage_reduction
            )
            total_damage += calculated_damage
            damage_report.append(
                f"            * {calculated_damage} {damage.damage_type} damage"
            )

        self.current_health_points -= total_damage

        # Log the detailed damage report
        logger.info(f"        * {self.name} took {total_damage} total damage:")
        for report in damage_report:
            logger.info(report)

        # Log the remaining health points
        logger.info(
            f"        * {self.name} now has {self.current_health_points} HP left."
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

    def get_trait_sources(self):
        """
        Returns a list of all sources of traits for this entity.
        This method can be overridden by subclasses to include additional sources.
        """
        # Start with the base traits (defined by Entity)
        traits = list(super().get_trait_sources())

        # Create a set to track seen traits and avoid duplicates
        seen_traits = {id(trait): trait for trait in traits}

        # Add traits from items, avoiding duplicates
        for item in self.item_manager.get_items():
            if item.traits:
                for trait in item.traits:
                    if id(trait) not in seen_traits:
                        traits.append(trait)
                        seen_traits[id(trait)] = trait

        return traits

    def update_traits(self):
        """
        Decrement the duration of each trait. If a trait expires (duration <= 0),
        remove it from the entity it is attached to and invalidate the entity's attribute cache.
        """
        super().update_traits()
        for item in self.item_manager.get_items():
            item.update_traits()

    @property
    def has_magic_weapon(self):
        """Returns True if any of the entity's weapons are magic; otherwise, False."""
        return any(item.is_magic for item in self.weapons)

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
        return self.current_health_points > self.death_door_threshold

    @property
    def is_bloodied(self) -> bool:
        # Always round up in DC20 (Core Rules Beta 0.8, page 39)
        return self.current_health_points <= math.ceil(self.max_health_points / 2)

    @property
    def is_well_bloodied(self) -> bool:
        return self.current_health_points <= math.ceil(self.max_health_points / 4)

    @property
    def is_at_death_door(self) -> bool:
        return (self.current_health_points < 0) & (
            self.current_health_points > self.death_door_threshold
        )

    @property
    def is_dead(self) -> bool:
        return not self.is_alive

    @property
    def items(self):
        return self.item_manager.get_items()

    def new_turn(self):
        """Implement all actions to be undertaken at the begining of an actor's turn."""
        self.is_full_dodging = False
        self.current_action_points -= self.attributes.true_damage_on_new_turn

    def end_turn(self):
        """Implement all actions to be undertaken at the end of an actor's turn."""
        return

    def new_round(self):
        self.update_traits()
        self.current_action_points = self.max_action_points
        self.reset_attack_count()
        self.reset_advantage_count()
        self.help_count = 0

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
