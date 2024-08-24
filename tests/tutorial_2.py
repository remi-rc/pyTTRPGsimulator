"""
This mini tutorial shows how to simulate a TTRPG combat.

DC20 was the TTRPG I had in mind when coding, so the name of the stats
match ! See https://thedungeoncoach.com/pages/dc20 for more on the game.
"""

# %% Import modules
import logging
from context import pyTTRPGsimulator as rpg

# Setup the logging to display more or less info
rpg.setup_logging(logging.INFO)


# %% Using our skills from tutorial_1.py, we can now seemlessly create actors and items

# These actors can have specific "combat strategies" :
strategies = [
    rpg.DefaultStrategy(),  # Efficient for combat
    rpg.DefaultDodgeStrategy(),  # Takes the "full dodge" action if target by enemies
    rpg.HelpAllyStrategy(),  # Will try to help an ally with the Help Action
    rpg.FullAttackStrategy(),  # Will attack recklessly as many times as action points allow
]

# The items of the characters are the following :
big_sword = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=2)])
sword = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=1)])
shield = rpg.Shield(physical_defense=2)
novice_armor = rpg.Armor(physical_defense=1)

# The player characters are the following :
Aldric = rpg.Actor(
    max_health_points=8,
    physical_defense=9,
    combat_mastery=1,
    might=3,
    items=[big_sword, novice_armor],
    combat_strategy=strategies[0],
    name="Aldric",
)

Liora = rpg.Actor(
    max_health_points=8,
    physical_defense=9,
    combat_mastery=1,
    agility=3,
    items=[sword, shield, novice_armor],
    combat_strategy=strategies[0],
    name="Liora",
)

Fynric = rpg.Actor(
    max_health_points=8,
    physical_defense=9,
    combat_mastery=1,
    charisma=3,
    items=[big_sword, novice_armor],
    combat_strategy=strategies[0],
    name="Fynric",
)

# The monster characters are the following :
claw_1 = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=1)])
claw_2 = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=2)])

Bear = rpg.Actor(
    max_health_points=20,
    physical_defense=11,
    might=3,
    combat_mastery=1,
    combat_strategy=strategies[3],
    name="Bear",
    items=[claw_2],
)

Wolf_1 = rpg.Actor(
    max_health_points=11,
    physical_defense=11,
    might=3,
    combat_mastery=1,
    combat_strategy=strategies[3],
    name="Wolf 1",
    items=[claw_1],
)

Wolf_2 = rpg.Actor(
    max_health_points=11,
    physical_defense=11,
    might=3,
    combat_mastery=1,
    combat_strategy=strategies[3],
    name="Wolf 2",
    items=[claw_1],
)

# %% We can now have them fight !
players = [Aldric, Liora, Fynric]
monsters = [Bear, Wolf_1, Wolf_2]


# If we want to log every action in the fight, we use the following :
combat_manager = rpg.CombatManager(players, monsters, initiative_dc=15)
combat_manager.reset_combat()
num_rounds, num_turns, winning_team, remaining_hp = combat_manager.run_combat()
print("num_rounds = ", num_rounds)
print("num_turns = ", num_turns)
print("winning_team = ", winning_team)
print(combat_manager.fight_debrief())

print("You should now have a 'game_logs.log' file containing the logs.")

# %% We can also repeat the fight a high number of times to obtain statistics
# We remove the logger

rpg.setup_logging(logging.WARNING)

N_combat = 5_000  # number of combats
num_rounds_list, num_turns_list, winrate_A, remaining_hp_list = rpg.run_simulations(
    N_combat, players, monsters, initiative_dc=15
)

# %% Summarize combat in a plot
rpg.plot_simulation_results(num_turns_list, winrate_A, remaining_hp_list)

print("Winrate of player characters = ", winrate_A)
