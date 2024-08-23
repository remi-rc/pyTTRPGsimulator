from copy import deepcopy
from typing import List, Optional, Union, Type
from .modifiers import DamageModifier, Resistance, Vulnerability
from .attributes import Attributes
from .traits import Trait
from dataclasses import fields, asdict


class Entity:
    def __init__(
        self,
        name: str = "",
        traits: Optional[Union[Trait, List[Trait]]] = None,
        attributes: "Attributes" = None,
        **kwargs,  # Defines the base attributes
    ):
        self.name = name

        # Ensure traits is always a list and validate each trait
        if isinstance(traits, Trait):
            self.base_traits = [deepcopy(traits)]
        elif isinstance(traits, list):
            for trait in traits:
                if not isinstance(trait, Trait):
                    raise TypeError(
                        f"All elements in 'traits' must be of type 'Trait'. Invalid element: {trait}"
                    )
            self.base_traits = traits
        elif traits is None:
            self.base_traits = []
        else:
            raise TypeError(
                f"'traits' must be a 'Trait' instance or a list of 'Trait' instances. Invalid element: {traits}"
            )

        # Cache for damage modifiers (resistance and vulnerabilities)
        self._cached_attributes = None
        self._cached_modifiers = {}

        # Update attributes with any custom values provided via kwargs
        self.base_attributes = attributes if attributes is not None else Attributes()
        for key, value in kwargs.items():
            if hasattr(self.base_attributes, key):
                setattr(self.base_attributes, key, value)
            else:
                raise AttributeError(f"'Attributes' object has no attribute '{key}'")

        self._generate_attribute_properties()

    def add_trait(self, traits: Union[Trait, List[Trait]]):
        if isinstance(traits, list):
            for trait in traits:
                self._add_single_trait(trait)
        else:
            self._add_single_trait(traits)
        self.invalidate_cache()

    def _add_single_trait(self, new_trait: Trait):
        for existing_trait in self.base_traits:
            if existing_trait.name == new_trait.name:
                # If the exact same trait is already in the list, update the duration
                existing_trait.duration = max(
                    existing_trait.duration, new_trait.duration
                )
                return

        # If the trait is not found, add it to the list
        self.base_traits.append(new_trait)

    def remove_trait(self, traits: Union[Trait, List[Trait]]):
        if isinstance(traits, list):
            for trait in traits:
                self._remove_single_trait(trait)
        else:
            self._remove_single_trait(traits)
        self.invalidate_cache()

    def _remove_single_trait(self, trait: Trait):
        if trait in self.base_traits:
            self.base_traits.remove(trait)

    def invalidate_cache(self):
        """
        Clear cached data and force recalculation of attributes and modifiers.
        """
        self._cached_modifiers.clear()
        self._cached_attributes = None

    def update_traits(self):
        """
        Decrement the duration of each trait. If a trait expires (duration <= 0),
        remove it and invalidate the entity's attribute cache.
        """
        expired_traits = []
        for trait in self.base_traits:
            trait.duration -= 1
            if trait.duration <= 0:
                expired_traits.append(trait)

        if expired_traits:
            self.invalidate_cache()
            self.remove_trait(expired_traits)

    def get_trait_sources(self) -> List[Trait]:
        """
        Returns a list of all active traits for this entity.
        """
        return self.base_traits

    def get_attribute_sources(self):
        """
        Returns a list of all sources of attributes for this entity.
        """
        return [self.base_attributes] + [trait.attributes for trait in self.traits]

    def aggregate_attributes(self):
        if self._cached_attributes is None:
            final_attributes = Attributes()
            for source in self.get_attribute_sources():
                final_attributes += source
            self._cached_attributes = final_attributes
        return self._cached_attributes

    def aggregate_modifiers(
        self, base_class: Type["DamageModifier"]
    ) -> List["DamageModifier"]:
        """
        Aggregate all modifiers of a specific base class from the entity's traits.
        """
        total_modifiers = []

        for trait in self.get_trait_sources():
            for modifier in trait.damage_modifiers:
                if issubclass(type(modifier), base_class):
                    total_modifiers.append(modifier)
        return total_modifiers

    def calculate_modifiers(
        self, modifier_class: Type[DamageModifier]
    ) -> List[DamageModifier]:
        """
        Retrieve cached modifiers of a specific class, populating cache if necessary.
        """
        if (modifier_class not in self._cached_modifiers) or (
            self._cached_modifiers is None
        ):
            self._cached_modifiers[modifier_class] = self.aggregate_modifiers(
                modifier_class
            )
        return self._cached_modifiers[modifier_class]

    @property
    def attributes(self) -> "Attributes":
        return self.aggregate_attributes()

    @property
    def traits(self) -> List["Trait"]:
        return self.get_trait_sources()

    @property
    def damage_modifiers(self) -> List["DamageModifier"]:
        return self.calculate_modifiers(DamageModifier)

    @property
    def resistances(self) -> List["Resistance"]:
        return self.calculate_modifiers(Resistance)

    @property
    def vulnerabilities(self) -> List["Vulnerability"]:
        return self.calculate_modifiers(Vulnerability)

    def _generate_attribute_properties(self):
        """
        Dynamically generate properties for each attribute in the Attributes class.
        """
        for field in self.base_attributes.__dataclass_fields__:
            # Create a property for each attribute in Attributes
            setattr(
                self.__class__,
                field,
                property(
                    fget=lambda self, key=field: getattr(self.attributes, key),
                    # Only the base attributes of an object are set
                    fset=lambda self, value, key=field: setattr(
                        self.base_attributes, key, value
                    ),
                ),
            )

    def __str__(self):
        non_standard_attributes = {}
        default_attributes = asdict(
            Attributes()
        )  # Get default attribute values as a dict

        # Check each attribute and compare with the default
        for field in fields(self.base_attributes):
            current_value = getattr(self.base_attributes, field.name)
            default_value = default_attributes[field.name]
            if current_value != default_value:
                non_standard_attributes[field.name] = current_value

        # Create a string representation of non-standard attributes
        attributes_str = ", ".join(
            f"{key}: {value}" for key, value in non_standard_attributes.items()
        )

        return f"{self.name}: {attributes_str if attributes_str else 'No non-standard attributes'}"
