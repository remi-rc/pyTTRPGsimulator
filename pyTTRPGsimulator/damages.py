from abc import ABC


class DamageType(ABC):
    """
    Abstract base class for damage types. This class should not be instantiated directly.
    Subclasses should implement specific types of damage.
    """

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self.__class__.__name__}"


def create_damage_class(class_name, base_class):
    """
    Dynamically create a subclass of a given base class with a specified name.

    Parameters:
        class_name (str): The name of the new class.
        base_class (type): The base class to inherit from.

    Returns:
        type: The newly created subclass.
    """

    class DamageSubclass(base_class):
        """
        A dynamically created subclass of the specified base class.
        """

        pass

    # Set the name of the subclass
    DamageSubclass.__name__ = class_name
    return DamageSubclass


# Create base damage type classes using create_damage_class
Physical = create_damage_class("Physical", DamageType)
Mystical = create_damage_class("Mystical", DamageType)

# Create specific damage type classes by dynamically subclassing Physical and Mystical
Bludgeoning = create_damage_class("Bludgeoning", Physical)
Cold = create_damage_class("Cold", Physical)
Corrosion = create_damage_class("Corrosion", Physical)
Fire = create_damage_class("Fire", Physical)
Lightning = create_damage_class("Lightning", Physical)
Piercing = create_damage_class("Piercing", Physical)
Poison = create_damage_class("Poison", Physical)
Slashing = create_damage_class("Slashing", Physical)
Psychic = create_damage_class("Psychic", Mystical)
Radiant = create_damage_class("Radiant", Mystical)
Sonic = create_damage_class("Sonic", Mystical)
Umbral = create_damage_class("Umbral", Mystical)


class Damage:
    """
    Represents damage with a specific type and value.
    """

    def __init__(self, damage_type: DamageType, value: float):
        """
        Initialize a Damage instance.

        Parameters:
            damage_type (DamageType): The type of damage.
            value (float): The amount of damage.

        Raises:
            TypeError: If damage_type is not an instance of DamageType.
        """
        if not isinstance(damage_type, DamageType):
            raise TypeError(
                f"damage_type must be an instance of DamageType, got {type(damage_type).__name__}"
            )
        self.damage_type = damage_type
        self.value = value

    def __str__(self):
        return f"{self.value} {self.damage_type.__class__.__name__} damage"

    def __repr__(self):
        return f"Damage(damage_type={self.damage_type.__class__.__name__}, value={self.value})"
