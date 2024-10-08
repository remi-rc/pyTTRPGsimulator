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
    def execute(self, source: "Actor", target: "Actor" = None, *args, **kwargs):
        """
        Executes the action. Must be implemented by subclasses.

        Parameters:
            source (Actor): The actor performing the action.
            target (List[Actor], optional): The target of the action.
        """
        pass


class GainAdvantage(Action):
    """
    Action to gain an advantage on your next attack.
    """

    def __init__(self, action_points_cost: int = 1):
        super().__init__(action_points_cost=action_points_cost)

    def execute(self, source: "Actor", target: "Actor" = None):
        if not self._apply_costs(source):
            return

        source.advantage_count += 1
        logger.info(f"{source.name} gains advantage. ({self.action_points_cost}AP)")
        logger.info(f"    * Advantage count is now {source.advantage_count}.")


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

    def execute(self, source: "Actor", target: "Actor"):
        if not self._apply_costs(source):
            return

        source.attack_count += 1
        advantage_count = source.advantage_count

        # Determine disadvantage based on dodging or full dodging status
        disadvantage_count = max(
            0, source.attack_count - source.max_attack_before_penalty
        )
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

        # General bonus (from bless)
        bonus_to_hit = source.get_bonus_roll()

        attack_tot = (
            attack_roll
            + source.prime_modifier
            + source.combat_mastery
            + source.one_time_hit_bonus
            + bonus_to_hit
        )
        is_critical_hit = attack_roll == source.critical_hit_threshold

        # Apply weapon styles and calculate total attack roll for the target
        # Assumes the actor uses the first weapon in their inventory
        if source.weapons:
            weapon = source.weapons[0]
        else:
            raise ValueError(f"{source.name} has no weapon equipped!")

        bonus_dmg_ws, bonus_hit_ws = weapon.apply_styles(target)
        attack_tot_target = attack_tot + bonus_hit_ws

        logger.info(
            f"{source.name} attacks {target.name} ! ({self.action_points_cost}AP)"
        )

        # Get precise logs for the rolls
        if source.one_time_hit_bonus > 0:
            if bonus_to_hit == 0:
                logger.info(
                    f"    {source.name} rolls a {attack_roll} + {source.prime_modifier} (prime) + {source.combat_mastery} (CM) + {source.one_time_hit_bonus} (Help)"
                )
            else:
                logger.info(
                    f"    {source.name} rolls a {attack_roll} + {source.prime_modifier} (prime) + {source.combat_mastery} (CM) + {source.one_time_hit_bonus} (Help) + {bonus_to_hit} (Bless)"
                )
        else:
            if bonus_to_hit == 0:
                logger.info(
                    f"    {source.name} rolls a {attack_roll} + {source.prime_modifier} (prime) + {source.combat_mastery} (CM)"
                )
            else:
                logger.info(
                    f"    {source.name} rolls a {attack_roll} + {source.prime_modifier} (prime) + {source.combat_mastery} (CM) + {bonus_to_hit} (Bless)"
                )

        # Remove any one-time hit bonus after it's used
        source.one_time_hit_bonus = 0

        if attack_tot_target >= target.physical_defense or is_critical_hit:
            logger.info(f"    {source.name}'s attack hits {target.name}.")

            if is_critical_hit:
                logger.info(f"        Critical hit !")

            if attack_tot_target >= target.physical_defense + 5:
                is_heavy_hit = True
                # The number of brutal hit "by 5"
                N_brutal_hit = (
                    int((attack_tot_target - target.physical_defense) // 5) - 1
                )
                damage_bonus = (
                    source.heavy_hit_damage + N_brutal_hit * source.brutal_hit_damage
                )
                if N_brutal_hit > 0:
                    logger.info(f"        Brutal hit !")
                else:
                    logger.info(f"        Heavy hit !")

            else:
                is_heavy_hit = False
                damage_bonus = 0

            if is_critical_hit:
                damage_bonus += source.critical_hit_damage

            # Add regular damage bonus from rage or other traits)
            damage_bonus += source.hit_damage
            for ij in range(len(weapon.damages)):
                if ij == 0:
                    total_damage = (
                        weapon.damages[ij].value + damage_bonus + bonus_dmg_ws
                    )
                else:
                    total_damage = weapon.damages[ij].value

                # A Heavy Hit or Critical Hit bypasses DR
                target.take_damage(
                    [
                        Damage(
                            damage_type=weapon.damages[ij].damage_type,
                            value=total_damage,
                        )
                    ],
                    ignore_damage_reduction=is_critical_hit + is_heavy_hit,
                )
        else:
            logger.info(f"    {source.name}'s attack missed {target.name}.")


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
    Action to target.

    Not fully implemented and integrated with the rest of the code.
    """

    def __init__(
        self,
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)

    def execute(self, source: "Actor", target: Optional["Actor"] = None):
        target = source if target is None else target
        if not self._apply_costs(source):
            return

        source.current_target = target
        logger.info(
            f"{source.name} now targets {target.name} ({self.action_points_cost}AP)."
        )


class MoveToTarget(Action):
    """
    Action to move toward a target.

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

        source.current_target = target
        logger.info(
            f"{source.name} moves to reach {target.name} ({self.action_points_cost}AP)."
        )


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
        logger.info(
            f"{source.name} prepares to dodge the next attack. ({self.action_points_cost}AP)"
        )


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
        logger.info(
            f"{source.name} prepares to dodge all the attacks.  ({self.action_points_cost}AP)"
        )


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

    def execute(self, source: "Actor", target: "Actor"):
        if not self._apply_costs(source):
            return

        if source.help_count == 0:
            bonus = random.randint(1, 8)  # Roll a 1d8 for the bonus
        elif source.help_count == 1:
            bonus = random.randint(1, 6)  # Roll a 1d6 for the bonus
        else:
            bonus = random.randint(1, 4)  # Roll a 1d4 for the bonus

        source.help_count += 1

        target.one_time_hit_bonus += bonus
        logger.info(
            f"{source.name} helps {target.name}.  ({self.action_points_cost}AP)"
        )


class ImposeTrait(Action):
    """
    Action to impose conditions on targets.
    """

    def __init__(
        self,
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
        traits: List["Trait"] = None,
    ):
        super().__init__(action_points_cost, mana_points_cost, stamina_points_cost)
        self.traits = traits if traits is not None else []

    def execute(self, source: "Actor", targets: List["Actor"]):
        if not self._apply_costs(source):
            return

        print(source.name)
        for target in targets:
            print(target.name)
            logger.info(f"{source.name} is imposing conditions on {target.name}")
            for trait in self.traits:
                logger.info(f"{source.name} imposes {trait.name} on {target.name}")
                target.add_trait(trait)


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
