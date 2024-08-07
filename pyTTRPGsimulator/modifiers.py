from abc import ABC
from typing import Type, List, Dict, Union, TYPE_CHECKING
import math

from .damages import DamageType

if TYPE_CHECKING:
    from .actors import Actor


class Modifier(ABC):
    """Base class for all modifiers."""

    def __init__(self, duration: int = math.inf):
        """
        Initialize a Modifier.

        Args:
            duration (int): The duration for which the modifier is active.
                            Defaults to infinity.
        """
        self.duration = duration

    def apply(self, actor: "Actor"):
        """
        Apply the modifier to an actor.

        Args:
            actor: The actor to which the modifier is applied.
        """
        actor.modifier_manager.add_modifier(self)
        actor.invalidate_caches()

    def remove(self, actor: "Actor"):
        """
        Remove the modifier from an actor.

        Args:
            actor: The actor from which the modifier is removed.
        """
        actor.modifier_manager.remove_modifier(self)
        actor.invalidate_caches()

    def decrease_duration(self):
        """
        Decrease the duration of the modifier.

        Returns:
            bool: True if the modifier should be removed, False otherwise.
        """
        if self.duration != math.inf:
            self.duration -= 1
            if self.duration <= 0:
                return True  # Indicate that the modifier should be removed
        return False


class ModifierManager:
    """Manages the modifiers for an actor."""

    def __init__(self):
        self.modifiers: Dict[Type[Modifier], List[Modifier]] = {}

    def add_modifier(self, modifier: Union[Modifier, List[Modifier]]):
        """
        Add a modifier or list of modifiers.

        Args:
            modifier (Union[Modifier, List[Modifier]]): The modifier or
            list of modifiers to be added.
        """
        if isinstance(modifier, list):
            for mod in modifier:
                self._add_single_modifier(mod)
        else:
            self._add_single_modifier(modifier)

    def _add_single_modifier(self, modifier: Modifier):
        """
        Add a single modifier.

        Args:
            modifier (Modifier): The modifier to be added.
        """
        mod_type = type(modifier)
        if mod_type not in self.modifiers:
            self.modifiers[mod_type] = []
        self.modifiers[mod_type].append(modifier)

    def remove_modifier(self, modifier: Union[Modifier, List[Modifier]]):
        """
        Remove a modifier or list of modifiers.

        Args:
            modifier (Union[Modifier, List[Modifier]]): The modifier or
            list of modifiers to be removed.
        """
        if isinstance(modifier, list):
            for mod in modifier:
                self._remove_single_modifier(mod)
        else:
            self._remove_single_modifier(modifier)

    def _remove_single_modifier(self, modifier: Modifier):
        """
        Remove a single modifier.

        Args:
            modifier (Modifier): The modifier to be removed.
        """
        mod_type = type(modifier)
        if mod_type in self.modifiers:
            if modifier in self.modifiers[mod_type]:
                self.modifiers[mod_type].remove(modifier)
            if not self.modifiers[mod_type]:
                del self.modifiers[mod_type]

    def has_modifier(self, modifier: Union[Type[Modifier], Modifier]) -> bool:
        """
        Check if a modifier is present.

        Args:
            modifier (Union[Type[Modifier], Modifier]): The modifier type
            or instance to check.

        Returns:
            bool: True if the modifier is present, False otherwise.
        """
        mod_type = modifier if isinstance(modifier, type) else type(modifier)
        return mod_type in self.modifiers and bool(self.modifiers[mod_type])

    def get_modifiers(
        self, modifier: Union[Type[Modifier], Modifier]
    ) -> List[Modifier]:
        """
        Get all modifiers of a given type.

        Args:
            modifier (Union[Type[Modifier], Modifier]): The modifier type or
            instance to retrieve.

        Returns:
            List[Modifier]: A list of modifiers of the given type.
        """
        mod_type = modifier if isinstance(modifier, type) else type(modifier)
        result = []
        for m_type, mods in self.modifiers.items():
            if issubclass(m_type, mod_type):
                result.extend(mods)
        return result

    def clear_modifiers(self):
        self.modifiers.clear()


class DefenseModifier(Modifier):
    """Modifier to adjust defenses."""

    def __init__(
        self,
        physical_defense: int = 0,
        mystical_defense: int = 0,
        physical_damage_reduction: int = 0,
        mystical_damage_reduction: int = 0,
        duration: int = math.inf,
    ):
        """
        Initialize a DefenseModifier.

        Args:
            physical_defense (int): The amount of physical defense provided.
                                    Defaults to 0.
            mystical_defense (int): The amount of mystical defense provided.
                                    Defaults to 0.
            physical_damage_reduction (int): The amount of physical DR provided.
                                    Defaults to 0.
            mystical_damage_reduction (int): The amount of mystical DR provided.
                                    Defaults to 0.
            duration (int): The duration of the modifier. Defaults to infinity.
        """
        super().__init__(duration)
        self.physical_defense = physical_defense
        self.mystical_defense = mystical_defense
        self.physical_damage_reduction = physical_damage_reduction
        self.mystical_damage_reduction = mystical_damage_reduction

    def __str__(self):
        return (
            f"DefenseModifier(Phys. defense={self.physical_defense}, "
            f"Myst. defense={self.mystical_defense}) "
        )

    def __repr__(self):
        return (
            f"DefenseModifier(Phys. defense={self.physical_defense}, "
            f"Myst. defense={self.mystical_defense}) "
        )


class DamageModifier(Modifier):
    """Modifier to adjust damage values."""

    def __init__(
        self,
        damage_type: DamageType,
        value: float,
        is_multiplicative: bool = False,
        duration: int = math.inf,
    ):
        """
        Initialize a DamageModifier.

        Args:
            damage_type (DamageType): The type of damage affected.
            value (float): The value of the modifier.
            is_multiplicative (bool): If True, the modifier is multiplicative.
                                      Defaults to False.
            duration (int): The duration of the modifier. Defaults to infinity.
        """
        super().__init__(duration)
        if (not isinstance(damage_type, DamageType)) and (
            not issubclass(damage_type, DamageType)
        ):
            raise TypeError(
                f"damage_type must be a subclass of DamageType, got {damage_type.__name__}"
            )
        self.damage_type = damage_type
        self.value = value
        self.is_multiplicative = is_multiplicative

    def __str__(self):
        return f"{self.__class__.__name__}(Damage Type={self.damage_type}, value={self.value}, is_multiplicative={self.is_multiplicative})"

    def __repr__(self):
        return f"{self.__class__.__name__}(Damage Type={self.damage_type}, value={self.value}, is_multiplicative={self.is_multiplicative})"


class Resistance(DamageModifier):
    """Modifier to add resistance to damage."""

    def __init__(
        self,
        damage_type: Type[DamageType],
        value: float,
        is_multiplicative: bool = False,
        duration: int = math.inf,
    ):
        """
        Initialize a Resistance modifier.

        Args:
            damage_type (Type[DamageType]): The type of damage affected.
            value (float): The value of the resistance.
            is_multiplicative (bool): If True, the resistance is multiplicative.
                                      Defaults to False.
            duration (int): The duration of the modifier. Defaults to infinity.

        Raises:
            ValueError: If the value is not between 0 and 1 for multiplicative resistance.
        """
        if is_multiplicative and (value > 1 or value < 0):
            raise ValueError(
                "For multiplicative resistance, the value must be between 0 and 1."
            )
        super().__init__(damage_type, value, is_multiplicative, duration)

    def __str__(self):
        return (
            f"Resistance to {type(self.damage_type).__name__}: {self.value} "
            f"({'Multiplicative' if self.is_multiplicative else 'Additive'})"
        )


class Vulnerability(DamageModifier):
    def __init__(
        self,
        damage_type: Type[DamageType],
        value: float,
        is_multiplicative: bool = False,
        duration: int = math.inf,
    ):
        """
        Initialize a Vulnerability modifier.

        Args:
            damage_type (Type[DamageType]): The type of damage affected.
            value (float): The value of the vulnerability.
            is_multiplicative (bool): If True, the vulnerability is multiplicative.
                                      Defaults to False.
            duration (int): The duration of the modifier. Defaults to infinity.

        Raises:
            ValueError: If the value is not greater than 1 for multiplicative vulnerability.
        """
        if is_multiplicative and value < 1:
            raise ValueError(
                "For multiplicative vulnerability, the value must be greater than 1."
            )
        super().__init__(damage_type, value, is_multiplicative, duration)

    def __str__(self):
        return (
            f"Vulnerability to {type(self.damage_type).__name__}: {self.value} "
            f"({'Multiplicative' if self.is_multiplicative else 'Additive'})"
        )
