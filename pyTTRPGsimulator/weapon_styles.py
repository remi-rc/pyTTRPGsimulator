from abc import ABC, abstractmethod
from .conditions import (
    Bleeding,
    Dazed,
    Exposed,
    Grappled,
    Hindered,
    Impaired,
    Petrified,
    Slowed,
)


class WeaponStyle(ABC):
    @abstractmethod
    def apply_effect(self, defender):
        bonus_damage = 0
        bonus_hit = 0
        return bonus_damage, bonus_hit

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self.__class__.__name__}"


class Axe_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Axe does +1 damage if the target is bleeding
        if any(isinstance(cond, Bleeding) for cond in defender.conditions):
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Bow_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Axe does +1 damage if the target is bleeding
        if any(isinstance(cond, Slowed) for cond in defender.conditions):
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Chained_style(WeaponStyle):
    pass


class Crossbow_style(WeaponStyle):
    pass


class Fist_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Axe does +1 damage if the target is bleeding
        if any(isinstance(cond, Grappled) for cond in defender.conditions):
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Hammer_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Axe does +1 damage if the target is bleeding
        if any(isinstance(cond, Dazed) for cond in defender.conditions) or any(
            isinstance(cond, Petrified) for cond in defender.conditions
        ):
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Pick_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Axe does +1 damage if the target is bleeding
        if any(isinstance(cond, Impaired) for cond in defender.conditions):
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Spear_style(WeaponStyle):
    pass


class Spear_style(WeaponStyle):
    pass


class Staff_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Axe does +1 damage if the target is bleeding
        if any(isinstance(cond, Hindered) for cond in defender.conditions) or any(
            isinstance(cond, Petrified) for cond in defender.conditions
        ):
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Sword_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Axe does +1 damage if the target is bleeding
        if any(isinstance(cond, Exposed) for cond in defender.conditions):
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Whip_style(WeaponStyle):
    pass
