"""
This mini tutorial shows how to include spells in your game.

Work in progress

"""

# %% Import modules
import logging
from context import pyTTRPGsimulator as rpg

# Setup the logging to display more or less info
rpg.setup_logging(logging.INFO)


# %% Create items and actors

# The items of the characters are the following :
big_sword = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=2)])
novice_armor = rpg.Armor(physical_defense=1)
claw_2 = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=2)])


# The player characters are the following :
Aldric = rpg.Actor(
    max_health_points=8,
    max_mana_points=10,
    physical_defense=9,
    combat_mastery=1,
    might=3,
    items=[big_sword, novice_armor],
    name="Aldric",
)

Liora = rpg.Actor(
    max_health_points=8,
    physical_defense=9,
    combat_mastery=1,
    agility=3,
    items=[big_sword, novice_armor],
    name="Liora",
)

Bear = rpg.Actor(
    max_health_points=20,
    physical_defense=11,
    might=3,
    combat_mastery=1,
    name="Bear",
    items=[claw_2],
)


# %% Create a bless Spell
# Note that in the future, the Spell class will be used instead of a specific Action
Bless_trait = rpg.Trait(name="Bless", duration=10, D4_roll_bonus=1)

Bless = rpg.Spell(
    traits=Bless_trait,
    concentration=True,
    action_points_cost=1,
    mana_points_cost=1,
    school="Abjuration",
    name="Bless",
)

# %% Aldric casts Bless on Liora and himself, and they then fight the bear

cast_spell_action = rpg.CastSpell()
cast_spell_action.execute(source=Aldric, targets=[Aldric, Liora], spell=Bless)

combat_manager = rpg.CombatManager([Aldric, Liora], [Bear], initiative_dc=10)

combat_manager.reset_combat()
num_rounds, num_turns, winning_team, remaining_hp = combat_manager.run_combat()
print("num_rounds = ", num_rounds)
print("num_turns = ", num_turns)
print("winning_team = ", winning_team)
print(combat_manager.fight_debrief())


# %% We can also repeat the fight a high number of times to obtain statistics
# This allows to compare the advantage procured by the bless spell (reset at each combat)

# We remove the logger
rpg.setup_logging(logging.WARNING)

N_combat = 5_000  # number of combats

# We make sure the Bless trait is not used by the actor
print("Aldric: ", [trait.name for trait in Aldric.traits])

print("Liora: ", [trait.name for trait in Liora.traits])

Aldric.remove_concentration()

print("Aldric: ", [trait.name for trait in Aldric.traits])

print("Liora: ", [trait.name for trait in Liora.traits])

num_rounds_list, num_turns_list, winrate_A, remaining_hp_list = rpg.run_simulations(
    N_combat, [Aldric, Liora], [Bear], initiative_dc=15
)
rpg.plot_simulation_results(num_turns_list, winrate_A, remaining_hp_list)

print("Winrate of player characters without Bless = ", winrate_A)


# We then add the Bless trait and run the combat again
cast_spell_action.execute(source=Aldric, targets=[Aldric, Liora], spell=Bless)
num_rounds_list, num_turns_list, winrate_A, remaining_hp_list = rpg.run_simulations(
    N_combat, [Aldric, Liora], [Bear], initiative_dc=15
)
rpg.plot_simulation_results(num_turns_list, winrate_A, remaining_hp_list)

print("Winrate of player characters with Bless = ", winrate_A)
