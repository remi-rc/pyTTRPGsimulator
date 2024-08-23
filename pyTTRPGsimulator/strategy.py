# Implement strategies for the actors
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from .actions import Action, GainAdvantage, Attack, Help, Full_Dodge
import random

if TYPE_CHECKING:
    from .actors import Actor


class Strategy(ABC):
    @abstractmethod
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        pass


class FullAttackStrategy(Strategy):
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        # Basic strategy example: always attack
        return Attack()


class DefaultStrategy(Strategy):
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
            return Attack()
        # If you counter your stacking disadvantage, attack
        if actor.advantage_count >= attack_count:
            return Attack()
        else:
            return GainAdvantage()


class DefaultDodgeStrategy(Strategy):
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        # Calculate actions based on remaining action points and advantages
        action_points = actor.action_points
        attack_count = actor.attack_count

        # If this actor is targeted by enemies, the full dodge action is taken
        if actor.targeting_enemies and not actor.is_full_dodging:
            return Full_Dodge()
        # Always attack if you have not yet attacked, or if it's your last action (otherwise it is wasted)
        if (attack_count == 0) or (action_points == 1):
            return Attack()
        # If you counter your stacking disadvantage, attack
        if actor.advantage_count >= attack_count:
            return Attack()
        else:
            return GainAdvantage()


class HelpAllyStrategy(Strategy):
    def choose_action(
        self,
        actor: "Actor",
        allies: List["Actor"],
        enemies: List["Actor"],
    ) -> Action:
        # Calculate actions based on remaining action points and advantages
        action_points = actor.action_points
        attack_count = actor.attack_count

        def is_ally_nearby(ally):
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

        # As your first action, help an ally
        if action_points == actor.max_action_points:
            # Select random ally that has not been helped yet and is nearby
            unhelped_nearby_allies = [
                ally
                for ally in allies
                if ally != actor and ally.help_count == 0 and is_ally_nearby(ally)
            ]
            if unhelped_nearby_allies:
                ally_to_help = random.choice(unhelped_nearby_allies)
                actor.current_target = ally_to_help
                return Help()

        # Always attack if you have not yet attacked, or if it's your last action (otherwise it is wasted)
        if (attack_count == 0) or (action_points == 1):
            return Attack()
        # If you counter your stacking disadvantage, attack
        if actor.advantage_count >= attack_count:
            return Attack()
        else:
            return GainAdvantage()
