__pyTTRGsimulator__



# Introduction

This code enables Dungeon Masters and players of table-top role player games (TTRPG) to simulate combats and predict the likelihood of a win, between two teams of "actors" (i.e., player characters, monsters). The code is quite general, but has been tailored to be used along the DC20 TTRPG. It has numerous features, some of them detailed below.

1. Creation of items (armors, weapons).
2. A damage system that can interact with resistance and vulnerabilities of actors.
3. A logger than can detail actions taken during a fight to see what happened.
4. A Strategy class, that details how an actor takes their actions.
5. A theater of the mind approach where no grid is required.

# Installation
Clone the repository:

git clone https://github.com/remi-rc/pyTTRPGsimulator.git

Or directly download it.

Add the library to your python path (system dependent)

# Usage

```
import pyTTRPGsimulator as rpg

epic_armor = rpg.Armor(
    physical_defense=2,
    mystical_defense=1,
    physical_damage_reduction=1,
    mystical_damage_reduction=1,
    name="Purple Dragon Hide",
)

Coach = rpg.Actor(
    health_points=8,
    physical_defense=8,
    combat_mastery=1,
    Might=3,
    equipped_items=[epic_armor],
    name="Coach",
)
```

See tutorials in the *tests* folder for more examples on how to run combats and create RPG elements.

# Limitations and future work

The code is far from being perfect, and currently has many limitations that I will be working on, with your help (see the How to Contribute section below).

1. The code is tailored for fights between "sword and board" characters, without really accounting for range weapons or spells during combat (even though range weapons and spells are implemented within the code already).
2. Reactions are not implemented yet.
3. An extension of the theater of the mind system to account for positioning would be a great addition to the gaming aspect of the simulator.
4. A more general approach to buffing / debuffing actors with Traits is required, in order to ease the implementation of features that can change almost every aspect of the game mechanics. For instance, using the Impact weapon property, a Heavy Hit is increased by one. This cannot yet be implemented seemlessly, because the heavy hit bonus of 1 was hard coded.
5. Examples and tutorials are still sparse.
6. Commenting of the code should be improved, giving examples within class definitions for example.

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