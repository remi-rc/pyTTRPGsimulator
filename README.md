__pyTTRGsimulator__



# Introduction

Welcome to pyTTRPGsimulator !
This code enables Dungeon Masters and players of table-top role playing games (TTRPG) to simulate combats and predict statistically the outcome of a fight between two teams of "actors" (i.e., player characters, monsters). The code is quite general, but has been tailored to be used with the [DC20 TTRPG](https://thedungeoncoach.com/pages/dc20). Note that pyTTRPGsimulator is not authorized or endorsed by DC20 (yet).

It has numerous features, some of them detailed below.

1. Creation of entities 
    _ Actors
        _ Monsters, Heros, PCs, Boss, etc.
    _ Items 
        _ Armors, weapons, shields, artifacts, etc.
2. A damage system that can interact with resistance and vulnerabilities of actors.
3. A logger than can detail actions taken during a fight to see what happened.
4. A Strategy class, that details how an actor takes their actions.
5. A Targeting class, that details how an actor preferentially selects their targets.
6. A theater of the mind approach where no grid is required.
7. The beginning of a Spell system, with concentration and spell duration being handled.

# Installation
Clone the repository:

git clone https://github.com/remi-rc/pyTTRPGsimulator.git

Or directly download it.

Add the library to your python path (system dependent)

# Basic usage

```python
import pyTTRPGsimulator as rpg

# Create a basic sword
sword_dmg = rpg.Damage(damage_type=rpg.Slashing(), 
                        value=2)
sword = rpg.Sword(name="Basic sword",
        damages=sword_dmg)

# Create some actors (PC and monster)
actor_1 = rpg.Actor(name="Coach", items=sword)
actor_2 = rpg.Actor(name="Penguin King", items=sword)

# Initialize the combat manager
combat_manager = rpg.CombatManager([actor_1], [actor_2], initiative_dc=10)

# Run the combat
combat_manager.run_combat()

# Print the outcome
print(combat_manager.fight_debrief())

```

# Advanced usage

```python
import pyTTRPGsimulator as rpg

# Create a complex magic item

# Immunity to fire damage
fire_immunity = rpg.Resistance(damage_type=rpg.Fire(), 
                    value=0, is_multiplicative=True)

# Use the Trait system to create complex features
ring_trait = rpg.Trait(name="Epic Ring Trait",
                    damage_modifiers=fire_immunity,
                    initiative=2,   # bonus to initiative
                    critical_hit_threshold=-1,  # crits on 19 and 20 !
                    )
# Instantiate the epic ring !
epic_ring = rpg.Item(name="Ring of the Penguin King", traits=ring_trait)

# Create a hero to wield this ring !
Coach = rpg.Actor(
    max_health_points=8,
    physical_defense=8,
    combat_mastery=1,
    Might=3,
    equipped_items=[epic_ring],
    name="Coach",
)
```

See tutorials in the *tests* folder for more examples on how to run combats and create RPG elements.

# Limitations and future work

The code is far from being perfect, and currently has many limitations that I will be working on, with your help (see the How to Contribute section below).

1. The code is tailored for fights between "sword and board" characters, without really accounting for range weapons or spells during combat (even though range weapons and spells are implemented within the code already).
    _ Spells can be cast before combat (accounts for concentration and spell duration)
2. Reactions are not implemented yet. A "Trigger" class should be created to handle more generally the case when things happen upon certain events.
3. An extension of the theater of the mind system to account for positioning would be a great addition to the gaming aspect of the simulator.
4. Examples and tutorials are still sparse.
5. Commenting of the code should be improved, giving examples within class definitions for example.

# How to Contribute


    Fork the repository
    Create a new branch (git checkout -b feature-branch)
    Commit your changes (git commit -am 'Add new feature')
    Push to the branch (git push origin feature-branch)
    Create a new Pull Request

You can also create a github issue.

# License

This project is licensed under the MIT License. See the LICENSE file for details.

# Contact
    GitHub: remi-rc
    Email: remi.necnor@gmail.com