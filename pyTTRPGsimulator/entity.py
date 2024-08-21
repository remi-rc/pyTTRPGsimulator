from typing import List, Optional, Union, Type
from .modifiers import DamageModifier, Resistance, Vulnerability
from .attributes import Attributes
from .traits import TraitsManager, Trait


class Entity:
    def __init__(
        self,
        name: str = "",
        traits: Optional[List["Trait"]] = None,
        attributes: "Attributes" = None,
        **kwargs,  # Defines the base attributes
    ):
        self.name = name

        self.traits_manager = TraitsManager(entity=self)
        self.traits_manager.add_trait(traits if traits is not None else [])

        # Cache for damage modifiers (resistance and vulnerabilities)
        self._cached_attributes = None
        self._cached_modifiers = {}

        # Update attributes with any custom values provided via kwargs
        self.base_attributes = attributes if attributes is not None else Attributes()
        for key, value in kwargs.items():
            if hasattr(self.attributes, key):
                setattr(self.attributes, key, value)
            else:
                raise AttributeError(f"'Attributes' object has no attribute '{key}'")

        self._generate_attribute_properties()

    @property
    def traits(self) -> List["Trait"]:
        return self.traits_manager.get_active_traits()

    @property
    def attributes(self) -> List["Trait"]:
        return self.aggregate_attributes()

    def add_trait(self, traits: Union[DamageModifier, List[DamageModifier]]):
        self.traits_manager.add_trait(traits if traits is not None else [])
        self.invalidate_cache()

    def remove_trait(self, traits: Union[DamageModifier, List[DamageModifier]]):
        self.traits_manager.remove_trait(traits if traits is not None else [])
        self.invalidate_cache()

    def invalidate_cache(self):
        """
        Clear cached data and force recalculation of attributes and modifiers.
        """
        self._cached_modifiers.clear()
        self._cached_attributes = None

    def aggregate_attributes(self):
        if self._cached_attributes is None:
            final_attributes = self.base_attributes
            for trait in self.traits:
                final_attributes += trait.attributes
            self._cached_attributes = final_attributes
            return final_attributes
        else:
            return self._cached_attributes

    def aggregate_modifiers(
        self, base_class: Type[DamageModifier]
    ) -> List[DamageModifier]:
        """
        Aggregate all modifiers of a specific base class from traits.
        """
        total_modifiers = []
        for trait in self.traits:
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
    def damage_modifiers(self) -> List["DamageModifier"]:
        return self.aggregate_modifiers(DamageModifier)

    @property
    def resistances(self) -> List["Resistance"]:
        return self.aggregate_modifiers(Resistance)

    @property
    def vulnerabilities(self) -> List["Vulnerability"]:
        return self.aggregate_modifiers(Vulnerability)

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
                    fset=lambda self, value, key=field: setattr(
                        self.attributes, key, value
                    ),
                ),
            )

    def __str__(self):
        return f"{self.name}: {self.attributes}"
