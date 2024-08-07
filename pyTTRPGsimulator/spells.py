from typing import List, Optional, TYPE_CHECKING

from .actions import CompositeAction

if TYPE_CHECKING:
    from .actions import Action
    from .actors import Actor


class Spell(CompositeAction):
    def __init__(
        self,
        actions: List["Action"] = None,
        action_points_cost: int = 1,
        mana_points_cost: int = 1,
        stamina_points_cost: int = 0,
        duration: int = 0,
        area: int = 0,
        distance: int = 0,
        school="",
        name="",
    ):
        super().__init__(
            actions, action_points_cost, mana_points_cost, stamina_points_cost
        )
        self.duration = duration
        self.area = area
        self.distance = distance
        self.school = school
        self.name = name
