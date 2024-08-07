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

# The player characters are the following :
sword = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=1)])
board = rpg.Shield(physical_damage_reduction=2)

Icarus = rpg.Actor(
    health_points=8,
    physical_defense=8,
    combat_mastery=1,
    Might=3,
    equipped_items=[sword, board],
    name="Icarus",
)

Claudio = rpg.Actor(
    health_points=8,
    physical_defense=8,
    combat_mastery=1,
    Might=3,
    equipped_items=[sword, board],
    name="Claudio",
)

Sui = rpg.Actor(
    health_points=8,
    physical_defense=8,
    combat_mastery=1,
    Might=3,
    equipped_items=[sword, board],
    name="Sui",
)

# The monster characters are the following :
claw_1 = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=1)])
claw_2 = rpg.MeleeWeapon(damages=[rpg.Damage(damage_type=rpg.Slashing(), value=2)])

Bear = rpg.Actor(
    health_points=20,
    physical_defense=11,
    Might=3,
    combat_mastery=1,
    name="Bear",
    equipped_items=[claw_2],
)

Wolf_1 = rpg.Actor(
    health_points=11,
    physical_defense=11,
    Might=3,
    combat_mastery=1,
    name="Wolf 1",
    equipped_items=[claw_1],
)

Wolf_2 = rpg.Actor(
    health_points=11,
    physical_defense=11,
    Might=3,
    combat_mastery=1,
    name="Wolf 2",
    equipped_items=[claw_1],
)

# %% We can now have them fight !
players = [Icarus, Claudio, Sui]
monsters = [Bear, Wolf_1, Wolf_2]


# If we want to log every action in the fight, we use the following :
combat_manager = rpg.CombatManager(players, monsters, initiative_dc=15)
combat_manager.reset_combat()
num_rounds, num_turns, winning_team, remaining_hp = combat_manager.run_combat()
print("num_rounds = ", num_rounds)
print("num_turns = ", num_turns)
print("winning_team = ", winning_team)
print(combat_manager.fight_debrief())

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


# %% Concluding remarks
"""
There are still many more things in the code that you could play with :

1/ The first is the Strategy, which you can add to an actor to indicate
how they fight. This has dramatic consequences on the winrate. 
The default strategy is kinda efficient already :)
actor.strategy chosen between :
    rpg.FullAttackStrategy(), rpg.DefaultStrategy(), rpg.HelpAllyStrategy()

2/ The second is closely related, and is the "target_mode" of an actor.
Some actors favor the weakest foes, while some favor the strongest, etc.
actor.target_mode chosen between :
    "target_weakest" (default), "target_strongest", "random"


You should now be equipped to roughly evaluate the influence of items, 
enemy numbers, initiative and a bunch of other variables :)

Try implementing an epic item from tutorial_1.py, adding it to an actor,
and see how this changes the outcome of the fight.

Add a bear and see how this changes the outcome of the fight.

You can reduce the number of action points of an actor at creation :

actor = rpg.actor(action_points=3)

or after creation 

actor.max_action_points = 3
"""
