import logging
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
import random

from .damages import Damage
from .traits import Trait

if TYPE_CHECKING:
    from .actors import Actor


# Set up logging
logger = logging.getLogger(__name__)


class Action(ABC):
    """
    Abstract base class for actions. Defines common attributes and methods for all actions.
    """

    def __init__(
        self,
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        self.action_points_cost = action_points_cost
        self.mana_points_cost = mana_points_cost
        self.stamina_points_cost = stamina_points_cost

    def _apply_costs(self, actor: "Actor"):
        """
        Deducts action costs from the actor if they have enough points.

        Parameters:
            actor (Actor): The actor performing the action.

        Returns:
            bool: True if the actor has enough points to perform the action, False otherwise.
        """
        if actor.current_action_points < self.action_points_cost:
            logger.warning(
                f"{actor.name} does not have enough action points to perform this action."
            )
            return False
        if actor.current_mana_points < self.mana_points_cost:
            print(actor.current_mana_points, self.mana_points_cost)
            logger.warning(
                f"{actor.name} does not have enough mana points to perform this action."
            )
            return False
        if actor.current_stamina_points < self.stamina_points_cost:
            logger.warning(
                f"{actor.name} does not have enough stamina points to perform this action."
            )
            return False

        actor.current_action_points -= self.action_points_cost
        actor.current_mana_points -= self.mana_points_cost
        actor.current_stamina_points -= self.stamina_points_cost
        return True

    @abstractmethod
    def execute(self, source: "Actor", targets: List["Actor"] = None, *args, **kwargs):
        """
        Executes the action. Must be implemented by subclasses.

        Parameters:
            source (Actor): The actor performing the action.
            targets (List[Actor], optional): The targets of the action.
        """
        pass


class GainAdvantage(Action):
    """
    Action to gain an advantage on your next attack.
    """

    def __init__(self, action_points_cost: int = 1):
        super().__init__(action_points_cost=action_points_cost)

    def execute(self, source: "Actor", targets: List["Actor"] = None):
        if not self._apply_costs(source):
            return

        source.advantage_count += 1
        logger.info(
            f"{source.name} gains advantage. Advantage count is now {source.advantage_count}."
        )


class Attack(Action):
    """
    Action to perform a simple attack.
    """

    def __init__(
        self,
        action_points_cost: int = 1,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", targets: List["Actor"]):
        if not self._apply_costs(source):
            return

        source.attack_count += 1
        advantage_count = source.advantage_count

        for target in targets:
            # Determine disadvantage based on dodging or full dodging status
            disadvantage_count = source.attack_count - 1
            if target.is_full_dodging or target.is_dodging:
                disadvantage_count += 1
                # Then remove "simple" dodging
                target.is_dodging = False

            # Determine the number of dice rolls based on advantage and disadvantage
            # Here, contrary to previous versions, each target gets its own attack roll
            rolls = [
                random.randint(1, 20)
                for _ in range(max(disadvantage_count + 1 - advantage_count, 1))
            ]

            if advantage_count > disadvantage_count:
                attack_roll = max(rolls)  # Use the highest roll due to advantage
                advantage_count = 0  # Reset advantage count after use
            else:
                attack_roll = min(rolls)  # Use the lowest roll due to disadvantage

            attack_tot = (
                attack_roll
                + source.prime_modifier
                + source.combat_mastery
                + source.one_time_hit_bonus
            )
            is_critical_hit = attack_roll == 20

            # Remove any one-time hit bonus after it's used
            source.one_time_hit_bonus = 0

            # Apply weapon styles and calculate total attack roll for the target
            # Assumes the actor uses the first weapon in their inventory
            weapon = source.weapons[0]
            bonus_dmg_ws, bonus_hit_ws = weapon.apply_styles(target)
            attack_tot_target = attack_tot + bonus_hit_ws

            if attack_tot_target >= target.physical_defense or is_critical_hit:
                logger.info(f"{source.name}'s attack hits {target.name}.")

                # TODO : handle brutal and heavy hit correctly
                damage_bonus = int((attack_tot_target - target.physical_defense) // 5)
                if is_critical_hit:
                    damage_bonus += source.critical_hit_damage

                for ij in range(len(weapon.damages)):
                    if ij == 0:
                        total_damage = (
                            weapon.damages[ij].value + damage_bonus + bonus_dmg_ws
                        )
                    else:
                        total_damage = weapon.damages[ij].value

                    target.take_damage(
                        [
                            Damage(
                                damage_type=weapon.damages[ij].damage_type,
                                value=total_damage,
                            )
                        ]
                    )
            else:
                logger.info(f"{source.name}'s attack missed {target.name}.")


class InflictDamage(Action):
    """
    Action to inflict damage directly.
    """

    def __init__(
        self,
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
        damages: List["Damage"] = None,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)
        self.damages = damages if damages is not None else []

    def execute(self, source: "Actor", targets: List["Actor"]):
        if not self._apply_costs(source):
            return

        for target in targets:
            logger.info(f"{source.name} inflicts damage on {target.name}")
            for damage in self.damages:
                logger.info(
                    f"{source.name} inflicts {damage.value} {damage.damage_type} damage to {target.name}"
                )
                target.take_damage([damage])
            logger.info(
                f"{target.name} has {target.current_health_points} health left."
            )


class Target(Action):
    """
    Action to target another actor.

    Not fully implemented and integrated with the rest of the code.

    # TODO : Maybe Target should be handled not by an Action...
    """

    def __init__(
        self,
        action_points_cost: int = 1,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", target: "Actor"):
        if target == source.current_target:
            return

        # It is free for a source to target an actor that is targeting the source
        if target.current_target == source:
            self.action_points_cost = 0
        # elif source.equipped_weapon and isinstance(source.equipped_weapon, RangeWeapon):  # TODO : implement weapon switch system

        # Since the cost can change, the check is made last
        if not self._apply_costs(source):
            return
        logger.info(f"{source.name} targets {target.name}")


class Move(Action):
    """
    Action to move in a given direction.

    Not fully implemented and integrated with the rest of the code.
    """

    def __init__(
        self,
        direction: str,
        action_points_cost: int = 1,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)
        self.direction = direction

    def execute(self, source: "Actor", target: Optional["Actor"] = None):
        target = source if target is None else target
        if not self._apply_costs(source):
            return

        logger.info(f"{source.name} moves {self.direction}")


class Disengage(Action):
    """
    Action to disengage from combat.

    Not fully implemented and integrated with the rest of the code.
    """

    def __init__(
        self,
        action_points_cost: int = 1,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", target: Optional["Actor"] = None):
        target = source if target is None else target
        if not self._apply_costs(source):
            return

        logger.info(f"{source.name} disengages from combat")


class Dodge(Action):
    """
    Action to dodge.
    """

    def __init__(
        self,
        action_points_cost: int = 1,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", target: Optional["Actor"] = None):
        target = source if target is None else target
        if not self._apply_costs(source):
            return

        target.is_dodging = True
        logger.info(f"{source.name} prepares to dodge the next attack.")


class Full_Dodge(Action):
    """
    Action to full dodge.
    """

    def __init__(
        self,
        action_points_cost: int = 2,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", target: Optional["Actor"] = None):
        target = source if target is None else target
        if not self._apply_costs(source):
            return

        target.is_full_dodging = True
        logger.info(f"{source.name} prepares to dodge all the attacks.")


class Grapple(Action):
    """
    Action to attempt to grapple a target.

    Not fully implemented and integrated with the rest of the code.
    """

    def __init__(
        self,
        action_points_cost: int = 1,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", targets: List["Actor"]):
        if not self._apply_costs(source):
            return

        for target in targets:
            logger.info(f"{source.name} attempts to grapple {target.name}")


class Help(Action):
    """
    Action to help allies, providing a hit bonus.
    """

    def __init__(
        self,
        action_points_cost: int = 1,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", targets: List["Actor"]):
        if not self._apply_costs(source):
            return

        if source.help_count == 0:
            bonus = random.randint(1, 8)  # Roll a 1d8 for the bonus
        elif source.help_count == 1:
            bonus = random.randint(1, 6)  # Roll a 1d6 for the bonus
        else:
            bonus = random.randint(1, 4)  # Roll a 1d4 for the bonus

        source.help_count += 1

        for ally in targets:
            ally.one_time_hit_bonus += bonus
            logger.info(f"{source.name} helps {ally.name}")


class ImposeTrait(Action):
    """
    Action to impose conditions on targets.
    """

    def __init__(
        self,
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
        status: List["Trait"] = None,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)
        self.status = status if status is not None else []

    def execute(self, source: "Action", targets: List["Action"]):
        if not self._apply_costs(source):
            return

        for target in targets:
            logger.info(f"{source.name} is imposing conditions on {target.name}")
            for status in self.status:
                logger.info(
                    f"{source.name} imposes {status.__class__.__name__} on {target.name}"
                )
                target.add_modifier(status)
            logger.info(
                f"{target.name} now has the following conditions: {target.modifier_manager.get_modifiers(Trait)}"
            )


class ImposeSavingThrow(Action):
    """
    Action to impose a saving throw check on targets.
    """

    def __init__(
        self,
        stat: str,
        difficulty: int,
        on_success: List["Action"],
        on_failure: List["Action"],
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)
        self.stat = stat
        self.difficulty = difficulty
        self.on_success = on_success
        self.on_failure = on_failure

    def execute(self, source: "Actor", targets: List["Actor"]):
        if not self._apply_costs(source):
            return

        for target in targets:
            roll = random.randint(1, 20)
            stat_value = getattr(target, self.stat, 0)
            total = roll + stat_value

            if total >= self.difficulty:
                logger.info(f"{target.name} succeeds on the {self.stat} saving throw")
                self._execute_actions(self.on_success, source, target)
            else:
                logger.info(f"{target.name} fails the {self.stat} saving throw")
                self._execute_actions(self.on_failure, source, target)

    def _execute_actions(
        self, actions: List["Action"], source: "Actor", target: "Actor"
    ):
        """
        Helper method to execute a list of actions.

        Parameters:
            actions (List[Action]): The actions to execute.
            source (Actor): The source of the actions, i.e., who pays the cost.
            target (Actor): The target of the actions.

        Nota Bene : for a "self" spell, source = target.
        """
        for action in actions:
            action.execute(source, [target])


class CompositeAction(Action):
    """
    Composite action to execute multiple actions sequentially.
    """

    def __init__(
        self,
        actions: List["Action"],
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)
        self.actions = actions

    def execute(self, source: "Actor", target: Optional["Actor"] = None):
        if not self._apply_costs(source):
            return

        for action in self.actions:
            action.execute(source, target)
