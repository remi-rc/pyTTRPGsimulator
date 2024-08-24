# Implement strategies for the actors
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from .actions import Action, GainAdvantage, Attack, Help, Full_Dodge
import random

if TYPE_CHECKING:
    from .actors import Actor

attack_action = Attack()
help_action = Help()
full_dodge_action = Full_Dodge()
gain_advantage_action = GainAdvantage()


class CombatStrategy(ABC):
    @abstractmethod
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        pass


class FullAttackStrategy(CombatStrategy):
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        # Basic strategy example: always attack
        return attack_action


class DefaultStrategy(CombatStrategy):
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        # Calculate actions based on remaining action points and advantages
        action_points = actor.current_action_points
        attack_count = actor.attack_count

        # Always attack if you have not yet attacked, or if it's your last action (otherwise it is wasted)
        if (attack_count == 0) or (action_points == 1):
            return attack_action
        # If you counter your stacking disadvantage, attack
        if actor.advantage_count >= attack_count:
            return attack_action
        else:
            return gain_advantage_action


class DefaultDodgeStrategy(CombatStrategy):
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        # Calculate actions based on remaining action points and advantages
        action_points = actor.current_action_points
        attack_count = actor.attack_count

        # If this actor is targeted by enemies, the full dodge action is taken
        if actor.targeting_enemies and not actor.is_full_dodging:
            return full_dodge_action
        # Always attack if you have not yet attacked, or if it's your last action (otherwise it is wasted)
        if (attack_count == 0) or (action_points == 1):
            return attack_action
        # If you counter your stacking disadvantage, attack
        if actor.advantage_count >= attack_count:
            return attack_action
        else:
            return gain_advantage_action


def is_ally_nearby(actor, ally, enemies):
    # Check if the ally is targeting the same target
    if (ally.current_target == actor.current_target) or (
        ally.current_target in enemies
    ):
        return True
    # Check if the ally is targeting an enemy that is targeting the actor
    for enemy in enemies:
        if enemy.current_target == actor or ally.current_target == enemy:
            return True
    return False


class HelpAllyStrategy(CombatStrategy):
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        # Calculate actions based on remaining action points and advantages
        action_points = actor.action_points
        attack_count = actor.attack_count

        # As your first action, help an ally
        if action_points == actor.max_action_points:
            # Select random ally that has not been helped yet and is nearby
            unhelped_nearby_allies = [
                ally
                for ally in allies
                if ally != actor
                and ally.help_count == 0
                and is_ally_nearby(actor, ally, enemies)
            ]
            if unhelped_nearby_allies:
                ally_to_help = random.choice(unhelped_nearby_allies)
                actor.current_target = ally_to_help
                return help_action

        # Always attack if you have not yet attacked, or if it's your last action (otherwise it is wasted)
        if (attack_count == 0) or (action_points == 1):
            return attack_action
        # If you counter your stacking disadvantage, attack
        if actor.advantage_count >= attack_count:
            return attack_action
        else:
            return gain_advantage_action
