from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
import random
from .actions import MoveToTarget, Target

move_to_target_action = MoveToTarget()
target_action = Target()

if TYPE_CHECKING:
    from .actors import Actor


class TargetingStrategy(ABC):
    """
    Abstract base class for different targeting strategies.
    """

    @abstractmethod
    def select_target(
        self, actor: "Actor", allies: List["Actor"], enemies: List["Actor"]
    ) -> Optional["Actor"]:
        pass


class TargetWeakestStrategy(TargetingStrategy):
    def select_target(
        self, actor: "Actor", allies: List["Actor"], enemies: List["Actor"]
    ) -> Optional["Actor"]:

        # Favor enemies targeting actor
        candidates = [enemy for enemy in enemies if enemy.current_target == actor]

        if actor.current_target in enemies and actor.current_target.is_alive:
            candidates.append(actor.current_target)

        # If no such enemy, select among all enemies
        if not candidates:
            candidates = enemies
            # The action to perform costs 1 AP
            action = move_to_target_action
        else:
            # The action to perform costs no AP
            action = target_action

        # Execute the action
        target = min(candidates, key=lambda enemy: enemy.current_health_points)

        # If already targeting the correct target, do nothing
        if target == actor.current_target:
            return

        action.execute(actor, target)
        return


class TargetHealthiestStrategy(TargetingStrategy):
    def select_target(
        self, actor: "Actor", allies: List["Actor"], enemies: List["Actor"]
    ) -> Optional["Actor"]:

        # Favor enemies targeting actor
        candidates = [enemy for enemy in enemies if enemy.current_target == actor]

        if actor.current_target in enemies and actor.current_target.is_alive:
            candidates.append(actor.current_target)

        # If no such enemy, select among all enemies
        if not candidates:
            candidates = enemies
            # The action to perform costs 1 AP
            action = move_to_target_action
        else:
            # The action to perform costs no AP
            action = target_action

        # Execute the action
        target = max(candidates, key=lambda enemy: enemy.current_health_points)

        # If already targeting the correct target, do nothing
        if target is actor.current_target:
            return

        action.execute(actor, target)
        return


class RandomTargetStrategy(TargetingStrategy):
    def select_target(
        self, actor: "Actor", allies: List["Actor"], enemies: List["Actor"]
    ) -> Optional["Actor"]:

        # Favor enemies targeting actor
        candidates = [enemy for enemy in enemies if enemy.current_target == actor]

        if actor.current_target in enemies and actor.current_target.is_alive:
            candidates.append(actor.current_target)

        # If no such enemy, select among all enemies
        if not candidates:
            candidates = enemies
            # The action to perform costs 1 AP
            action = move_to_target_action
        else:
            # The action to perform costs no AP
            action = target_action

        # Execute the action
        target = random.choice(candidates) if candidates else None

        # If already targeting the correct target, do nothing
        if target is actor.current_target:
            return

        action.execute(actor, target)
        return
