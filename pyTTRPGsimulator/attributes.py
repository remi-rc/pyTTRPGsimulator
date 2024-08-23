from dataclasses import dataclass, fields


@dataclass
class Attributes:
    physical_defense: int = 0
    mystical_defense: int = 0
    physical_damage_reduction: int = 0
    mystical_damage_reduction: int = 0

    max_health_points: int = 0
    max_stamina_points: int = 0
    max_grit_points: int = 0
    max_mana_points: int = 0

    death_door_HP_threshold = 0

    might: int = 0
    agility: int = 0
    intelligence: int = 0
    charisma: int = 0

    prime_modifier_bonus: int = 0

    might_save: int = 0
    agility_save: int = 0
    intelligence_save: int = 0
    charisma_save: int = 0

    might_check: int = 0
    agility_check: int = 0
    intelligence_check: int = 0
    charisma_check: int = 0

    initiative: int = 0
    move_speed: int = 0

    # positive for advantage, negative for disadvantage
    might_adv: int = 0
    agility_adv: int = 0
    intelligence_adv: int = 0
    charisma_adv: int = 0

    combat_mastery: int = 0
    spell_DC: int = 0

    max_action_points: int = 0
    max_attack_before_penalty: int = 0
    critical_hit_damage: int = 0
    critical_hit_threshold: int = 0  # negative value to reduce the threshold
    heavy_hit_damage: int = 0
    brutal_hit_damage: int = 0
    death_threshold: int = 0

    mastery_light_armor: bool = False
    mastery_heavy_armor: bool = False

    is_magic: bool = False

    true_damage_on_new_turn = 0

    # Conditions
    is_bleeding: bool = False
    is_blinded: bool = False
    is_burning: bool = False
    is_charmed: bool = False
    is_dazed: bool = False
    is_deafened: bool = False
    is_doomed: bool = False
    is_exposed: bool = False
    is_frightened: bool = False
    is_grappled: bool = False
    is_hindered: bool = False
    is_impaired: bool = False
    is_incapacitated: bool = False
    is_intimidated: bool = False
    is_invisible: bool = False
    is_paralyzed: bool = False
    is_petrified: bool = False
    is_prone: bool = False

    def __add__(self, other: "Attributes") -> "Attributes":
        if not isinstance(other, Attributes):
            return NotImplemented

        result = Attributes()
        for field in fields(self):
            field_name = field.name
            current_value = getattr(self, field_name)
            other_value = getattr(other, field_name)

            if isinstance(current_value, bool) and isinstance(other_value, bool):
                # Use logical OR for boolean attributes
                setattr(result, field_name, current_value or other_value)
            elif isinstance(current_value, int) and isinstance(other_value, int):
                # Use addition for integer attributes
                setattr(result, field_name, current_value + other_value)
            else:
                raise TypeError(f"Unsupported type for field '{field_name}': {type(current_value)}")

        return result


actor_attributes = Attributes(
    physical_defense=8,
    mystical_defense=8,
    max_health_points=10,
    max_action_points=4,
    heavy_hit_damage=1,
    brutal_hit_damage=1,
    critical_hit_damage=2,
    max_attack_before_penalty=1,
    move_speed=5,
    critical_hit_threshold=20,
    mastery_light_armor=True,
)
