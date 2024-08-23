from typing import List, Optional, Union
from .damages import Damage
from .modifiers import DamageModifier, Resistance, Vulnerability
from .weapon_styles import *
from .entity import Entity
from .traits import Trait
from .attributes import Attributes


class Item(Entity):
    def __init__(
        self,
        name: str = "",
        traits: Optional[List["Trait"]] = None,
        attributes: "Attributes" = None,
        **kwargs,
    ):
        super().__init__(name=name, traits=traits, attributes=attributes, **kwargs)

    def __str__(self) -> str:
        # Extract and format resistances and vulnerabilities
        resistances = []
        vulnerabilities = []

        for mod in self.damage_modifiers:
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
        return f"Item(name={self.name}, is_magic={self.is_magic}, modifiers={self.damage_modifiers})"


class ItemManager:
    def __init__(self):
        self.items: List[Item] = []

    def add_item(self, item: Union[Item, List[Item]]):
        if isinstance(item, list):
            for i in item:
                if i not in self.items:
                    self.items.append(i)
        else:
            if item not in self.items:
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

    def __repr__(self):
        return (
            f"Armor(name={self.name}, physical_defense={self.attributes.physical_defense}, "
            f"mystical_defense={self.attributes.mystical_defense}, "
            f"physical_damage_reduction={self.attributes.physical_damage_reduction}, "
            f"mystical_damage_reduction={self.attributes.mystical_damage_reduction}, "
            f"modifiers={self.damage_modifiers})"
        )

    def __str__(self) -> str:
        base_str = super().__str__()
        return (
            f"{base_str}\n"
            f"Physical Defense: {self.attributes.physical_defense}\n"
            f"Mystical Defense: {self.attributes.mystical_defense}\n"
            f"Physical Damage Reduction: {self.attributes.physical_damage_reduction}\n"
            f"Mystical Damage Reduction: {self.attributes.mystical_damage_reduction}"
        )


class Shield(Armor):

    def __repr__(self):
        return (
            f"Shield(name={self.name}, physical_defense={self.attributes.physical_defense}, "
            f"mystical_defense={self.attributes.mystical_defense}, "
            f"physical_damage_reduction={self.attributes.physical_damage_reduction}, "
            f"mystical_damage_reduction={self.attributes.mystical_damage_reduction}, "
            f"modifiers={self.damage_modifiers})"
        )


class Weapon(Item):
    def __init__(
        self,
        name: str = "",
        traits: Optional[List["Trait"]] = None,
        attributes: "Attributes" = None,
        damages: List["Damage"] = None,
        weapon_range: int = 1,
        weapon_styles: Optional[List["WeaponStyle"]] = None,
        **kwargs,
    ):

        # Ensure damages is a list
        if damages is None:
            raise TypeError("Expected a Damage instance or a list of Damage instances.")
        elif isinstance(damages, Damage):
            self.damages = [damages]
        elif isinstance(damages, list) and all(isinstance(d, Damage) for d in damages):
            self.damages = damages
        else:
            raise TypeError("Expected a Damage instance or a list of Damage instances.")
            print(damages)

        self.weapon_range = weapon_range
        self.weapon_styles = weapon_styles if weapon_styles is not None else []

        super().__init__(name=name, traits=traits, attributes=attributes, **kwargs)

    def apply_styles(self, defender):
        bonus_damage_tot, bonus_hit_tot = 0, 0
        print("defender : ", defender)
        for style in self.weapon_styles:
            bonus_damage, bonus_hit = style.apply_effect(self=style, defender=defender)  # TODO : check why such call is required ?!
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
        name: str = "",
        damages: List["Damage"] = None,
        weapon_range: int = 1,
        traits: Optional[List["Trait"]] = None,
        attributes: "Attributes" = None,
        weapon_styles: Optional[List["WeaponStyle"]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            damages=damages,
            weapon_range=weapon_range,
            traits=traits,
            attributes=attributes,
            weapon_styles=weapon_styles,
            **kwargs,
        )

    def __str__(self):
        return f"Melee Weapon\n" + super().__str__()


class RangeWeapon(Weapon):

    def __str__(self):
        return f"Range Weapon\n" + super().__str__()


def create_weapon_class(weapon_name, weapon_style):
    class Weapon(MeleeWeapon):
        def __init__(
            self,
            name: str = "",
            damages: List["Damage"] = None,
            weapon_range: int = 1,
            traits: Optional[List["Trait"]] = None,
            attributes: "Attributes" = None,
            **kwargs,
        ):
            super().__init__(
                name=name,
                damages=damages,
                weapon_range=weapon_range,
                traits=traits,
                attributes=attributes,
                weapon_styles=[weapon_style],
                **kwargs,
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
