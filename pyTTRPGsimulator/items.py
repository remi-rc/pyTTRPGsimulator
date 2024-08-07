from typing import List, Optional, Union
from .damages import Damage, Physical, Mystical
from .modifiers import Modifier, DefenseModifier, Resistance, Vulnerability
from .weapon_styles import *


class Item:
    def __init__(
        self,
        modifiers: Optional[List["Modifier"]] = None,
        is_magic=False,
        name: str = "",
    ):
        self.name = name
        self.modifiers = modifiers if modifiers is not None else []
        self.is_magic = is_magic  # By default, items are not magic

    def add_modifier(self, modifier: Modifier):
        if isinstance(modifier, list):
            self.modifiers.extend(modifier)
        else:
            self.modifiers.append(modifier)

    def remove_modifier(self, modifier: Modifier):
        if isinstance(modifier, list):
            for mod in modifier:
                if mod in self.modifiers:
                    self.modifiers.remove(mod)
        else:
            if modifier in self.modifiers:
                self.modifiers.remove(modifier)

    def __str__(self) -> str:
        # Extract and format resistances and vulnerabilities
        resistances = []
        vulnerabilities = []

        for mod in self.modifiers:
            if isinstance(mod, Resistance):
                if mod.is_multiplicative:
                    resistances.append(
                        f"Resistance to {type(mod.damage_type).__name__}: {mod.value} (Multiplicative)"
                    )
                else:
                    resistances.append(
                        f"Resistance to {type(mod.damage_type).__name__}: {mod.value} (Additive)"
                    )
            elif isinstance(mod, Vulnerability):
                if mod.is_multiplicative:
                    vulnerabilities.append(
                        f"Vulnerability to {type(mod.damage_type).__name__}: {mod.value} (Multiplicative)"
                    )
                else:
                    vulnerabilities.append(
                        f"Vulnerability to {type(mod.damage_type).__name__}: {mod.value} (Additive)"
                    )

        resistances_str = "\n".join(resistances) if resistances else "None"
        vulnerabilities_str = "\n".join(vulnerabilities) if vulnerabilities else "None"

        return (
            f"{self.name}\n"
            f"Magic : {'Yes' if self.is_magic else 'No'}\n"
            f"{resistances_str}\n"
            f"{vulnerabilities_str}\n"
        )

    def __repr__(self):
        return f"Item(name={self.name}, is_magic={self.is_magic}, modifiers={self.modifiers})"


class ItemManager:
    def __init__(self):
        self.items: List[Item] = []

    def add_item(self, item: Union[Item, List[Item]]):
        if isinstance(item, list):
            self.items.extend(item)
        else:
            self.items.append(item)

    def remove_item(self, item: Union[Item, List[Item]]):
        if isinstance(item, list):
            for i in item:
                if i in self.items:
                    self.items.remove(i)
        else:
            if item in self.items:
                self.items.remove(item)

    def get_items(self) -> List[Item]:
        return self.items

    def get_items_of_type(self, item_type: type) -> List[Item]:
        return [item for item in self.items if isinstance(item, item_type)]


class Armor(Item):
    def __init__(
        self,
        physical_defense: int = 0,
        mystical_defense: int = 0,
        physical_damage_reduction: int = 0,
        mystical_damage_reduction: int = 0,
        modifiers: Optional[List["Modifier"]] = None,
        is_magic=False,
        name: str = "",
    ):

        base_modifiers = []

        if physical_defense > 0:
            base_modifiers.append(DefenseModifier(physical_defense=physical_defense))

        if mystical_defense > 0:
            base_modifiers.append(DefenseModifier(mystical_defense=mystical_defense))

        if physical_damage_reduction > 0:
            base_modifiers.append(
                DefenseModifier(physical_damage_reduction=physical_damage_reduction)
            )

        if mystical_damage_reduction > 0:
            base_modifiers.append(
                DefenseModifier(mystical_damage_reduction=mystical_damage_reduction)
            )

        if modifiers:
            base_modifiers.extend(modifiers)

        super().__init__(base_modifiers, is_magic, name)

        self.physical_damage_reduction = physical_damage_reduction
        self.mystical_damage_reduction = mystical_damage_reduction

    def __str__(self):
        base_str = super().__str__()
        return (
            f"{base_str}\nPhysical Defense: {self.base_physical_defense}\n"
            f"Mystical Defense: {self.base_mystical_defense}\n"
            f"Physical Damage Reduction: {self.physical_damage_reduction}\n"
            f"Mystical Damage Reduction: {self.mystical_damage_reduction}"
        )


class Shield(Armor):
    def __init__(
        self,
        physical_defense: int = 0,
        mystical_defense: int = 0,
        physical_damage_reduction: int = 0,
        mystical_damage_reduction: int = 0,
        modifiers: Optional[List["Modifier"]] = None,
        is_magic=False,
        name: str = "",
    ):

        super().__init__(
            physical_defense,
            mystical_defense,
            physical_damage_reduction,
            mystical_damage_reduction,
            modifiers,
            is_magic,
            name,
        )

    def __str__(self):
        return f"Shield\n" + super().__str__()


class Weapon(Item):
    def __init__(
        self,
        damages: List[Damage],
        weapon_range: int,
        modifiers: Optional[List["Modifier"]] = None,
        weapon_styles: Optional[List[WeaponStyle]] = None,
        is_magic=False,
        name: str = "",
    ):
        super().__init__(modifiers, is_magic, name)
        self.damages = damages
        self.weapon_range = weapon_range
        self.weapon_styles = weapon_styles if weapon_styles is not None else []

    def apply_styles(self, defender):
        bonus_damage_tot, bonus_hit_tot = 0, 0
        for style in self.weapon_styles:
            bonus_damage, bonus_hit = style.apply_effect(defender)
            bonus_damage_tot += bonus_damage
            bonus_hit_tot += bonus_hit
        return bonus_damage_tot, bonus_hit_tot

    def __str__(self):
        damages_str = ", ".join(str(damage) for damage in self.damages)
        weapon_styles_str = ", ".join(str(style) for style in self.weapon_styles)
        base_str = super().__str__()
        return (
            f"{base_str}\nDamages: {damages_str}\nRange: {self.weapon_range}\n"
            f"Styles: {weapon_styles_str}"
        )


class MeleeWeapon(Weapon):
    def __init__(
        self,
        damages: List[Damage],
        weapon_range: int = 1,
        modifiers: Optional[List["Modifier"]] = None,
        weapon_styles: Optional[List["WeaponStyle"]] = None,
        is_magic=False,
        name: str = "",
    ):
        super().__init__(
            damages, weapon_range, modifiers, weapon_styles, is_magic, name
        )

    def __str__(self):
        return f"Melee Weapon\n" + super().__str__()


class RangeWeapon(Weapon):
    def __init__(
        self,
        damages: List[Damage],
        weapon_range: int = 6,
        modifiers: Optional[List["Modifier"]] = None,
        weapon_styles: Optional[List["WeaponStyle"]] = None,
        is_magic=False,
        name: str = "",
    ):
        super().__init__(
            damages, weapon_range, modifiers, weapon_styles, is_magic, name
        )

    def __str__(self):
        return f"Range Weapon\n" + super().__str__()


def create_weapon_class(weapon_name, weapon_style):
    class Weapon(MeleeWeapon):
        def __init__(
            self,
            damages: List[Damage],
            weapon_range: int = 1,
            modifiers: Optional[List["Modifier"]] = None,
            is_magic=False,
            name: str = "",
        ):
            super().__init__(
                damages, weapon_range, modifiers, [weapon_style], is_magic, name
            )

    Weapon.__name__ = weapon_name
    return Weapon


# Define your weapon classes
Axe = create_weapon_class("Axe", Axe_style)
Sword = create_weapon_class("Sword", Sword_style)
Bow = create_weapon_class("Bow", Bow_style)
Chained = create_weapon_class("Chained", Chained_style)
Crossbow = create_weapon_class("Crossbow", Crossbow_style)
Fist = create_weapon_class("Fist", Fist_style)
Hammer = create_weapon_class("Hammer", Hammer_style)
Pick = create_weapon_class("Pick", Pick_style)
Spear = create_weapon_class("Spear", Spear_style)
Staff = create_weapon_class("Staff", Staff_style)
Whip = create_weapon_class("Whip", Whip_style)
