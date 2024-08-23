from abc import ABC, abstractmethod


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
        if defender.is_bleeding:
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Bow_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Bow does +1 damage if the target is slowed
        if defender.is_slowed:
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
        # Fist does +1 damage if the target is grappled
        if defender.is_grappled:
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Hammer_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Hammer does +1 damage if the target is dazed or petrified
        if defender.is_dazed or defender.is_petrified:
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Pick_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Pick does +1 damage if the target is impaired
        if defender.is_impaired:
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
        # Staff does +1 damage if the target is hindered or petrified
        if defender.is_hindered or defender.is_petrified:
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Sword_style(WeaponStyle):
    def apply_effect(self, defender):
        bonus_hit = 0
        bonus_damage = 0
        # Sword does +1 damage if the target is exposed
        if defender.is_exposed:
            bonus_damage = 1
        return bonus_damage, bonus_hit


class Whip_style(WeaponStyle):
    pass
