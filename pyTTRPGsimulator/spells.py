from typing import List, Optional, Union, TYPE_CHECKING
from copy import deepcopy

from .actions import Action
from .traits import Trait
from .damages import Damage


if TYPE_CHECKING:
    from .actions import Action
    from .actors import Actor


class Spell:
    def __init__(
        self,
        traits: Optional[Union[Trait, List[Trait]]] = None,
        traits_on_save: Optional[Union[Trait, List[Trait]]] = None,
        traits_on_fail: Optional[Union[Trait, List[Trait]]] = None,
        damages_on_save: List["Damage"] = None,
        damages_on_fail: List["Damage"] = None,
        action_points_cost: int = 0,
        mana_points_cost: int = 0,
        stamina_points_cost: int = 0,
        concentration: bool = False,
        save_charac=None,
        area: int = 0,
        distance: int = 0,
        school="",
        name="",
    ):

        # Convert single traits to a list if needed
        self.traits = [traits] if isinstance(traits, Trait) else (traits or [])
        self.traits_on_save = (
            [traits_on_save]
            if isinstance(traits_on_save, Trait)
            else (traits_on_save or [])
        )
        self.traits_on_fail = (
            [traits_on_fail]
            if isinstance(traits_on_fail, Trait)
            else (traits_on_fail or [])
        )

        # Initialize damages lists, default to empty lists if not provided
        self.damages_on_save = damages_on_save or []
        self.damages_on_fail = damages_on_fail or []

        # Initialize other attributes
        self.action_points_cost = action_points_cost
        self.mana_points_cost = mana_points_cost
        self.stamina_points_cost = stamina_points_cost
        self.concentration = concentration
        self.save_charac = save_charac
        self.area = area
        self.distance = distance
        self.school = school
        self.name = name

        # This field is dynamically updated upon casting the spell
        self.targets = None


class CastSpell(Action):
    """
    Composite action to execute multiple actions sequentially.

    TODO : could probably improve inheritance pattern
    """

    def __init__(self):
        return

    def execute(self, source: "Actor", targets: "Actor", spell: "Spell"):
        self.action_points_cost = spell.action_points_cost
        self.mana_points_cost = spell.mana_points_cost
        self.stamina_points_cost = spell.stamina_points_cost

        if not self._apply_costs(source):
            return

        # If concentration is required, assign spell to actor
        if spell.concentration:
            spell_copy = deepcopy(spell)
            spell_copy.targets = targets
            source.add_concentration(spell_copy)

        # Apply all traits on all targets
        for trait in spell.traits:
            for target in targets:
                target.add_trait(trait)

        # Save-related traits
        if (
            spell.traits_on_save
            or spell.traits_on_fail
            or spell.damages_on_save
            or spell.damages_on_fail
        ):
            for target in targets:
                # If succeeds on save
                if target.roll_save(spell.save_charac) >= source.spell_DC:
                    if spell.traits_on_save:
                        target.add_trait(spell.traits_on_save)
                    if spell.damages_on_save:
                        target.take_damage(spell.damages_on_save)

                # If fails on save
                else:
                    if spell.traits_on_fail:
                        target.add_trait(spell.traits_on_fail)
                    if spell.damages_on_fail:
                        target.take_damage(spell.damages_on_fail)
