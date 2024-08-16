"""
This mini tutorial shows how to create basic elements of a TTRPG.

DC20 was the TTRPG I had in mind when coding, so the name of the stats
match ! See https://thedungeoncoach.com/pages/dc20 for more on the game.
"""

# %% Import modules
import logging
from context import pyTTRPGsimulator as rpg

# Setup the logging to display more or less info
rpg.setup_logging(logging.WARNING)


# %% Create a character: all stats have a default
Remi = rpg.Actor(
    health_points=8,
    physical_defense=8,
    combat_mastery=1,
    Might=3,
    Agility=1,
    Charisma=-1,
    name="Remi",
)

# You can print some important info of the actor as follows
print(Remi)

# Note that the Actor class does not know the character creation rules, so you can input almost anything (at your own risk)

# %% Create an item
# Our hero is a little too weak right now. Let's add some armor and weapon !

# Armors can give more than "physical_defense"
epic_armor = rpg.Armor(
    physical_defense=2,
    mystical_defense=1,
    physical_damage_reduction=1,
    mystical_damage_reduction=1,
    name="Purple Dragon Hide",
)

nice_shield = rpg.Shield(physical_defense=2, name="Penguin Bone Shield")

# To create a weapon, we have a lot of freedom
# We can create instances of the Damage class to represent damages with their types
fire_dmg = rpg.Damage(damage_type=rpg.Fire(), value=1)
slashing_dmg = rpg.Damage(damage_type=rpg.Slashing(), value=1)
epic_weapon = rpg.MeleeWeapon(
    damages=[slashing_dmg, fire_dmg], name="My epic fire sword"
)

# Since it is a sword, we can add the sword style to it
epic_weapon.weapon_styles = [rpg.Sword_style()]


# Maybe the weapon is enchanted, and provides a resistance to cold damage ? Resist X=1
resist_cold = rpg.Resistance(damage_type=rpg.Cold(), value=1)

# But maybe the weapon will also give vulnerability to fire damage ? Vulnerability Double
vulnerability_fire = rpg.Vulnerability(
    damage_type=rpg.Fire(), value=2, is_multiplicative=True
)

# We can now add these attributes to the weapon
epic_weapon.add_modifier(resist_cold)
epic_weapon.add_modifier(vulnerability_fire)

# ... and print to check some properties
print(epic_weapon, "\n")


# %% Finally, we can add the items to our hero :
Remi.add_item([epic_armor, nice_shield, epic_weapon])

# and we can print again to check the actor has updated :
print(Remi)


# %% Note that we can also create an actor directly equipped
Remi = rpg.Actor(
    health_points=8,
    physical_defense=8,
    combat_mastery=1,
    Might=3,
    equipped_items=[epic_armor, nice_shield, epic_weapon],
    name="Remi",
)

print(Remi)
