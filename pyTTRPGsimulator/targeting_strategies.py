from abc import ABC, abstractmethod
from typing import List, Optional


class TargetingStrategy(ABC):
    """
    Abstract base class for different targeting strategies.
    """

    @abstractmethod
    def select_target(
        self, actor: "Actor", candidates: List["Actor"]
    ) -> Optional["Actor"]:
        pass


import random


class TargetWeakestStrategy(TargetingStrategy):
    def select_target(
        self, actor: "Actor", candidates: List["Actor"]
    ) -> Optional["Actor"]:
        return (
            min(candidates, key=lambda enemy: enemy.current_health_points)
            if candidates
            else None
        )


class TargetStrongestStrategy(TargetingStrategy):
    def select_target(
        self, actor: "Actor", candidates: List["Actor"]
    ) -> Optional["Actor"]:
        return (
            max(candidates, key=lambda enemy: enemy.current_health_points)
            if candidates
            else None
        )


class RandomTargetStrategy(TargetingStrategy):
    def select_target(
        self, actor: "Actor", candidates: List["Actor"]
    ) -> Optional["Actor"]:
        return random.choice(candidates) if candidates else None
