import logging
from typing import List, Optional, Type, Dict, Union
import math
import random

from .items import Item, Armor, Weapon, ItemManager
from .damages import Damage, Physical
from .modifiers import (
    Modifier,
    ModifierManager,
    Resistance,
    Vulnerability,
    DefenseModifier,
)
from .conditions import Condition
from .strategy import DefaultStrategy

# Set up logging
logger = logging.getLogger(__name__)

logger.info("This is a test info message from module actors")
logger.error("This is a test error message from module actors")


class Actor:
    def __init__(
        self,
        name: str = "",
        health_points: int = 1,
        stamina_points: int = 0,
        grit_points: int = 0,
        mana_points: int = 0,
        Might: int = 0,
        Agility: int = 0,
        Intelligence: int = 0,
        Charisma: int = 0,
        combat_mastery: int = 0,
        physical_defense: int = 8,
        mystical_defense: int = 8,
        equipped_items: Optional[List["Item"]] = None,
        base_modifiers: Optional[List["Modifier"]] = None,
        profficiencies: Optional[List["Item"]] = None,
        death_threshold: int = -3,
        move_speed: int = 5,
        action_points: int = 4,
        crit_dmg_bonus: int = 2,
        target_mode: str = "target_weakest",
        strategy=DefaultStrategy(),
    ):
        """
        Initialize an Actor with various attributes and properties.

        Parameters:
            name (str): The name of the actor. Default is an empty string.
            health_points (int): The initial and maximum health points of the actor. Default is 1.
            stamina_points (int): The initial and maximum stamina points of the actor. Default is 0.
            grit_points (int): The initial and maximum grit points of the actor. Default is 0.
            mana_points (int): The initial and maximum mana points of the actor. Default is 0.
            Might (int): The Might attribute of the actor, representing physical strength. Default is 0.
            Agility (int): The Agility attribute of the actor, representing speed and dexterity. Default is 0.
            Intelligence (int): The Intelligence attribute of the actor, representing mental acuity. Default is 0.
            Charisma (int): The Charisma attribute of the actor, representing social influence. Default is 0.
            combat_mastery (int): The combat mastery level of the actor, usually half the character's level, rounded up. Default is 0.
            physical_defense (int): The base physical defense rating of the actor. Default is 8.
            mystical_defense (int): The base mystical defense rating of the actor. Default is 8.
            equipped_items (Optional[List[Item]]): A list of items the actor is initially equipped with. Default is None.
            base_modifiers (Optional[List[Modifier]]): A list of base modifiers applied to the actor. Default is None.
            profficiencies (Optional[List[Item]]): A list of items the actor is proficient with. Default is None.
            death_threshold (int): The health threshold below which the actor is considered dead. Default is -3.
            move_speed (int): The movement speed of the actor. Default is 5.
            action_points (int): The maximum action points the actor can use in a turn. Default is 4.
            crit_dmg_bonus (int): The bonus damage applied when the actor scores a critical hit. Default is 2.
            target_mode (str): The targeting mode of the actor, determining how they select targets. Default is "target_weakest".
            strategy (Strategy): The strategy used by the actor to decide actions in combat. Default is DefaultStrategy().
        """
        # Statistics
        self.name = name
        self.max_health_points = health_points
        self.health_points = health_points
        self.max_stamina_points = stamina_points
        self.stamina_points = stamina_points
        self.max_grit_points = grit_points
        self.grit_points = grit_points
        self.max_mana_points = mana_points
        self.mana_points = mana_points

        # Attributes
        self.Might = Might
        self.Agility = Agility
        self.Intelligence = Intelligence
        self.Charisma = Charisma
        self.combat_mastery = combat_mastery  # 1/2 your character's level, rounded up

        self.base_physical_defense = physical_defense
        self.base_mystical_defense = mystical_defense

        # Items and modifier management
        self.item_manager = ItemManager()
        if equipped_items:
            self.item_manager.add_item(equipped_items)

        self.base_modifiers = base_modifiers if base_modifiers is not None else []
        self.profficiencies = profficiencies if profficiencies is not None else []

        # Modifier manager
        self.modifier_manager = ModifierManager()
        self.modifier_manager.add_modifier(self.base_modifiers)

        # Dynamic cache
        self._dynamic_cache: Dict[Type[Modifier], List[Modifier]] = {}

        # Rarely changed caracteristics
        self.death_threshold = death_threshold
        self.move_speed = move_speed
        self.max_action_points = action_points
        self.action_points = action_points
        self.crit_dmg_bonus = crit_dmg_bonus

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

    def __str__(self) -> str:
        equipped_items_str = (
            ", ".join(item.name for item in self.item_manager.get_items())
            if self.item_manager.get_items()
            else "None"
        )
        return (
            f"Actor: {self.name}\n"
            f"Health: {self.health_points}/{self.max_health_points}\n"
            f"Stamina: {self.stamina_points}/{self.max_stamina_points}\n"
            f"Grit: {self.grit_points}/{self.max_grit_points}\n"
            f"Mana: {self.mana_points}/{self.max_mana_points}\n"
            f"Might: {self.Might}\n"
            f"Agility: {self.Agility}\n"
            f"Intelligence: {self.Intelligence}\n"
            f"Charisma: {self.Charisma}\n"
            f"Combat Mastery: {self.combat_mastery}\n"
            f"Physical Defense: {self.physical_defense}\n"
            f"Mystical Defense: {self.mystical_defense}\n"
            f"Physical Damage Reduction: {self.physical_damage_reduction}\n"
            f"Mystical Damage Reduction: {self.mystical_damage_reduction}\n"
            f"Move Speed: {self.move_speed}\n"
            f"Action Points: {self.action_points}/{self.max_action_points}\n"
            f"Critical Damage Bonus: {self.crit_dmg_bonus}\n"
            f"Target Mode: {self.target_mode}\n"
            f"Equipped Items: {equipped_items_str}\n"
        )

    def reset_attack_count(self):
        self.attack_count = 0

    def reset_advantage_count(self):
        self.advantage_count = 0

    def update_targeting(self, team_allies: List["Actor"], team_enemies: List["Actor"]):
        """
        Update the current target of the actor based on the given allies and enemies.
        """
        # TODO : check why following comment breaks the combat
        # if (self.current_target) and (self.current_target.health_points >= 0) and (self.current_target in team_enemies):
        #     print("Already selecting a valid target")
        #     return

        # Remove target if allied actor (because of Help, Heal, Mind Control, etc)
        if self.current_target in team_allies:
            self.current_target = None

        # Check if current target is dead
        if self.current_target and self.current_target.health_points <= 0:
            # Since we untarget enemy, we remove actor from list of targeting enemies
            self.current_target.targeting_enemies.remove(self)
            self.current_target = None

        # Filter out dead enemies
        alive_enemies = [enemy for enemy in team_enemies if enemy.health_points > 0]

        # Determine enemies targeting this actor
        enemies_targeting_me = [
            enemy
            for enemy in self.targeting_enemies
            if (enemy.current_target == self) and enemy.is_alive
        ]

        # Determine the weakest ally who is still alive
        alive_allies = [ally for ally in team_allies if ally.health_points > 0]
        weakest_ally = min(
            alive_allies, key=lambda ally: ally.health_points, default=None
        )

        if enemies_targeting_me:
            # If there are enemies targeting this actor, select among them based on target_mode
            self.current_target = self.select_target(enemies_targeting_me)
        elif (
            self.target_mode == "help_ally"
            and weakest_ally
            and weakest_ally.current_target
            and weakest_ally.current_target.health_points > 0
        ):
            # If help ally mode, target the same enemy as the weakest ally
            self.current_target = weakest_ally.current_target
        else:
            # Select freely among all alive enemies
            self.current_target = self.select_target(alive_enemies)

        if self.current_target:
            # We add actor to the list of targeting enemies :
            self.current_target.targeting_enemies.append(self)
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
        """TODO : improve in order to indicate for each actor which stat is considered."""
        roll = random.randint(1, 20)
        logger.info(f"{self.name} rolls {roll}")
        return roll

    def aggregate_modifiers(self, base_class: Type[Modifier]) -> List[Modifier]:
        """
        Aggregate all modifiers of a specific base class from items and modifiers.
        """
        total_modifiers = []
        for item in self.item_manager.get_items():
            for modifier in item.modifiers:
                if issubclass(type(modifier), base_class):
                    total_modifiers.append(modifier)
        total_modifiers.extend(
            mod
            for mod_list in self.modifier_manager.modifiers.values()
            for mod in mod_list
            if issubclass(type(mod), base_class)
        )
        return total_modifiers

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
            self.mystical_damage_reduction
            if not isinstance(damage.damage_type, Physical)
            else self.physical_damage_reduction
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
        self.health_points -= total_damage
        logger.info(
            f"    {self.name} took {total_damage} {damage.damage_type} damage and has {self.health_points} HP left."
        )

    def add_item(self, item: Union[Item, List[Item]]):
        """
        Add an item or list of items to the actor's inventory.
        """
        self.item_manager.add_item(item)
        self.invalidate_modifiers_cache()

    def remove_item(self, item: Union[Item, List[Item]]):
        """
        Remove an item or list of items from the actor's inventory.
        """
        self.item_manager.remove_item(item)
        self.invalidate_modifiers_cache()

    def saving_throw(self, stat, dc):
        """
        Perform a saving throw based on the given stat and difficulty challenge (dc).
        """
        if stat not in ["Might", "Agility", "Intelligence", "Charisma"]:
            raise ValueError(
                "Invalid stat. Choose from 'Might', 'Agility', 'Intelligence', 'Charisma'."
            )

        stat_value = getattr(self, stat)
        save_roll = random.randint(1, 20) + stat_value
        success = save_roll >= dc

        return success, save_roll

    @property
    def prime_modifier(self) -> int:
        """
        Return the highest attribute value among Might, Agility, Intelligence, and Charisma.
        """
        return max([self.Might, self.Agility, self.Intelligence, self.Charisma])

    @property
    def weapons(self) -> List["Weapon"]:
        """
        Return a list of weapons in the actor's inventory.

        TODO : implement a real inventory system to allow an
        actor to switch weapon as part of their strategy. For
        instance, actor could alternate between range and melee,
        to kite an ennemy. #longTermGoal
        """
        return self.item_manager.get_items_of_type(Weapon)

    @property
    def armors(self) -> List["Armor"]:
        """
        Return a list of armors in the actor's inventory.
        """
        return self.item_manager.get_items_of_type(Armor)

    def get_cached_modifiers(self, modifier_class: Type[Modifier]) -> List[Modifier]:
        """
        Retrieve cached modifiers of a specific class, populating cache if necessary.
        """
        if modifier_class not in self._dynamic_cache:
            self._dynamic_cache[modifier_class] = self.aggregate_modifiers(
                modifier_class
            )
        return self._dynamic_cache[modifier_class]

    @property
    def is_alive(self) -> bool:
        """
        Check if the actor is alive.
        """
        return self.health_points > 0

    @property
    def modifiers(self) -> List["Modifier"]:
        """
        Return a list of all active modifiers on the actor.
        """
        return self.get_cached_modifiers(Modifier)

    @property
    def resistances(self) -> List["Resistance"]:
        """
        Return a list of all active resistances on the actor.
        """
        return self.get_cached_modifiers(Resistance)

    @property
    def vulnerabilities(self) -> List["Vulnerability"]:
        """
        Return a list of all active vulnerabilities on the actor.
        """
        return self.get_cached_modifiers(Vulnerability)

    @property
    def conditions(self) -> List["Condition"]:
        """
        Return a list of all active conditions on the actor.
        """
        return self.get_cached_modifiers(Condition)

    @property
    def physical_defense(self) -> int:
        """
        Calculate and return the actor's total physical defense.
        """
        total_defense = self.base_physical_defense
        for modifier in self.aggregate_modifiers(DefenseModifier):
            total_defense += modifier.physical_defense
        return total_defense

    @property
    def mystical_defense(self) -> int:
        """
        Calculate and return the actor's total mystical defense.
        """
        total_defense = self.base_mystical_defense
        for modifier in self.aggregate_modifiers(DefenseModifier):
            total_defense += modifier.mystical_defense
        return total_defense

    @property
    def physical_damage_reduction(self) -> int:
        """
        Calculate and return the actor's total physical defense.
        """
        total_DR = 0
        for modifier in self.aggregate_modifiers(DefenseModifier):
            total_DR += modifier.physical_damage_reduction
        return total_DR

    @property
    def mystical_damage_reduction(self) -> int:
        """
        Calculate and return the actor's total mystical defense.
        """
        total_DR = 0
        for modifier in self.aggregate_modifiers(DefenseModifier):
            total_DR += modifier.mystical_damage_reduction
        return total_DR

    # Modifier checks
    def add_modifier(self, modifier: Union["Modifier", List["Modifier"]]):
        """
        Add a modifier or list of modifiers to the actor.
        """
        self.modifier_manager.add_modifier(modifier)
        self.invalidate_modifiers_cache()

    def remove_modifier(self, modifier: Union["Modifier", List["Modifier"]]):
        """
        Remove a modifier or list of modifiers from the actor.

        Comment: for now, you need to input the exact variable
        used to place the modifier, not just its type.
        """
        self.modifier_manager.remove_modifier(modifier)
        self.invalidate_modifiers_cache()

    def has_modifier(self, modifier_type: Type["Modifier"]) -> bool:
        """
        Check if the actor has a specific type of modifier.
        """
        return self.modifier_manager.has_modifier(modifier_type)

    def invalidate_modifiers_cache(self):
        self._dynamic_cache.clear()

    def new_turn(self):
        """Implement all actions to be undertaken at the begining of an actor's turn."""
        self.is_full_dodging = False

    def end_turn(self):
        """Implement all actions to be undertaken at the end of an actor's turn."""
        return

    def new_round(self):
        """
        Sequence of updates at the start of a new round for the actor.
        """
        self.action_points = self.max_action_points
        self.update_modifiers()
        self.reset_attack_count()
        self.reset_advantage_count()
        self.help_count = 0  # number of times the actor has provided help this round
        pass

    def update_modifiers(self):
        """
        Update the duration of modifiers and remove expired ones.
        """
        expired_modifiers = []
        for modifier in self.modifiers:
            if modifier.decrease_duration():
                expired_modifiers.append(modifier)

        for modifier in expired_modifiers:
            self.remove_modifier(modifier)
            logger.info(f"{self.name} has lost the modifier: {modifier}")

    def full_rest(self):
        """
        Restore all attributes to their maximum values, simulating a full rest.
        """
        self.health_points = self.max_health_points
        self.stamina_points = self.max_stamina_points
        self.grit_points = self.max_grit_points
        self.mana_points = self.max_mana_points
        self.action_points = self.max_action_points
        self.reset_attack_count()
        self.reset_advantage_count()
        self.help_count = 0
        logger.info(f"{self.name} has fully rested and all attributes are restored.")
