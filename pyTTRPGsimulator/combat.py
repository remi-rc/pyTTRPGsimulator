import logging
from typing import List
from .actors import Actor
from .actions import Attack, Help, GainAdvantage
import matplotlib.pyplot as plt

# Set up logging
logger = logging.getLogger(__name__)

attack_action = Attack()


class CombatManager:
    def __init__(
        self, team_a: List["Actor"], team_b: List["Actor"], initiative_dc: int
    ):
        """
        Initialize the CombatManager with two teams and a difficulty class (DC) for initiative rolls.

        Parameters:
            team_a (List[Actor]): List of actors in team A.
            team_b (List[Actor]): List of actors in team B.
            initiative_dc (int): Difficulty challenge for determining initiative.
        """
        self.team_a = team_a
        self.team_b = team_b
        self.initiative_dc = initiative_dc
        self.turn_order: List["Actor"] = []
        self.current_turn_index = 0
        self.has_initiative = False
        self.rounds_count = 0
        self.turns_count = 0

        # Mark teams for each actor
        for actor in team_a:
            actor.is_team_A = True
        for actor in team_b:
            actor.is_team_A = False

    def roll_initiative(self):
        """
        Roll for initiative to determine the turn order of actors in combat.
        """
        logger.info(f"")
        logger.info(f"Rolling for initiative:")
        team_a_initiatives = [(actor, actor.roll_initiative()) for actor in self.team_a]
        team_a_initiatives.sort(key=lambda x: x[1], reverse=True)

        team_b_initiatives = [(actor, actor.roll_initiative()) for actor in self.team_b]
        team_b_initiatives.sort(key=lambda x: x[1], reverse=True)

        highest_player_initiative = (
            team_a_initiatives[0][1] if team_a_initiatives else 0
        )

        if highest_player_initiative >= self.initiative_dc:
            # Players win initiative
            self.turn_order = self.determine_turn_order(
                team_a_initiatives, team_b_initiatives, monsters_win=False
            )
        else:
            # Monsters win initiative
            self.turn_order = self.determine_turn_order(
                team_a_initiatives, team_b_initiatives, monsters_win=True
            )
        logger.info(f"")
        logger.info(f"Turn order determined:")
        for idx, actor in enumerate(self.turn_order, 1):
            logger.info(f"{idx}/ {actor.name}")
        logger.info(f"")

        self.has_initiative = True

        return

    def determine_turn_order(
        self,
        team_a_initiatives: List[tuple],
        team_b_initiatives: List[tuple],
        monsters_win: bool,
    ) -> List[Actor]:
        """
        Determine the turn order based on initiative rolls.

        Parameters:
            team_a_initiatives (List[tuple]): List of tuples containing team A actors and their initiative rolls.
            team_b_initiatives (List[tuple]): List of tuples containing team B actors and their initiative rolls.
            monsters_win (bool): Flag indicating whether monsters (team B) win the initiative.

        Returns:
            List[Actor]: The ordered list of actors for the combat turns.
        """
        turn_order = []
        player_index = 0
        monster_index = 0

        while player_index < len(team_a_initiatives) and monster_index < len(
            team_b_initiatives
        ):
            if monsters_win:
                turn_order.append(team_b_initiatives[monster_index][0])
                monster_index += 1
                monsters_win = False
            else:
                turn_order.append(team_a_initiatives[player_index][0])
                player_index += 1
                monsters_win = True

        # Add remaining actors if any
        while player_index < len(team_a_initiatives):
            turn_order.append(team_a_initiatives[player_index][0])
            player_index += 1

        while monster_index < len(team_b_initiatives):
            turn_order.append(team_b_initiatives[monster_index][0])
            monster_index += 1

        return turn_order

    def get_allies_enemies(self, actor):
        """
        Get the allies and enemies of a given actor.

        Parameters:
            actor (Actor): The actor for whom to find allies and enemies.

        Returns:
            tuple: A tuple containing two lists - allies and enemies.
        """
        if actor.is_team_A:
            allies = self.team_a
            enemies = self.team_b
        else:
            allies = self.team_b
            enemies = self.team_a
        return allies, enemies

    def update_targeting(self, actor):
        """
        Update the target of a given actor based on current allies and enemies.

        Parameters:
            actor (Actor): The actor whose targeting needs to be updated.
        """
        allies, enemies = self.get_allies_enemies(actor)
        actor.update_targeting(allies, enemies)

    def next_turn_actor(self):
        """
        Get the next actor to take a turn in the combat.

        Returns:
            Actor: The next actor to take a turn, or None if the combat is over.
        """
        # Fight is over if turn order is None or contains one Actor only
        if not self.turn_order:
            return None
        elif len(self.turn_order) == 1:
            return None

        # Loop to find the next alive actor
        while True:
            current_actor = self.turn_order[self.current_turn_index]
            self.current_turn_index = (self.current_turn_index + 1) % len(
                self.turn_order
            )

            if self.current_turn_index == 0:
                self.rounds_count += 1

            # If the current actor is alive, proceed with their turn
            if current_actor.is_alive:
                self.update_targeting(current_actor)
                return current_actor

            # If all actors are dead, return None to indicate no more turns
            if all(not actor.is_alive for actor in self.turn_order):
                return None

    def run_round(self):
        """
        Run a single round of combat.
        """
        self.rounds_count += 1
        # Reset action points for all actors
        for actor in self.turn_order:
            actor.new_round()

        for _ in range(len(self.turn_order)):
            current_actor = self.next_turn_actor()
            if current_actor:
                self.execute_turn(current_actor)
                # Only increment turn count if a turn has been played
                self.turns_count += 1
            if self.is_combat_over():
                break

        # Remove dead actors from the turn order (a bit buggy)
        # self.turn_order = [actor for actor in self.turn_order if actor.is_alive]

    def run_combat(self):
        """
        Run the combat until it is over, logging the result.

        Returns:
            tuple: A tuple containing the number of rounds, number of turns, the winning team, and remaining health points.
        """
        if not self.has_initiative:
            self.roll_initiative()

        while not self.is_combat_over():
            self.log_alive_actors()
            self.run_round()

        logger.info(f"")
        logger.info(f"Fight is over !")

        winning_team = "A" if any(actor.is_alive for actor in self.team_a) else "B"
        remaining_hp = {
            actor.name: actor.health_points for actor in self.team_a + self.team_b
        }

        num_rounds = self.rounds_count
        num_turns = self.turns_count
        return num_rounds, num_turns, winning_team, remaining_hp

    def execute_turn(self, actor: "Actor"):
        """
        Execute the turn for a given actor.

        Parameters:
            actor (Actor): The actor whose turn is to be executed.
        """
        logger.info(f"")
        logger.info(f"{actor.name}'s turn:")

        if not actor.current_target:
            self.update_targeting(actor)
        elif actor.current_target.health_points <= 0:
            self.update_targeting(actor)

        while (
            actor.action_points > 0
            and actor.current_target.health_points > 0
            and not self.is_combat_over()
        ):
            allies, enemies = self.get_allies_enemies(actor)

            # Reselect enemy if current target is an ally (because of Help action or Healing)
            if actor.current_target in allies:
                self.update_targeting(actor)

            action = actor.strategy.choose_action(actor, allies, enemies)
            if isinstance(action, GainAdvantage):
                action.execute(actor)
            elif isinstance(action, Attack):
                action.execute(actor, [actor.current_target])
            elif isinstance(action, Help):
                action.execute(actor, [actor.current_target])

            # Reselect enemy if current enemy is dead
            if actor.current_target.health_points <= 0:
                self.update_targeting(actor)

            if self.is_combat_over():
                return

    def is_combat_over(self):
        """
        Check if the combat is over.

        Returns:
            bool: True if the combat is over, False otherwise.
        """
        team_a_alive = any(actor.health_points > 0 for actor in self.team_a)
        team_b_alive = any(actor.health_points > 0 for actor in self.team_b)
        return not (team_a_alive and team_b_alive)

    def log_alive_actors(self):
        """
        Log the status of all alive actors.
        """
        alive_actors = [actor for actor in self.team_a + self.team_b if actor.is_alive]
        logger.info(f"")
        logger.info(f"################ NEW ROUND ################")
        logger.info(f"Alive actors at round {self.rounds_count}:")
        for actor in alive_actors:
            logger.info(f"Actor: {actor.name}, Health Points: {actor.health_points}")

    def fight_debrief(self) -> str:
        """
        Generate a debrief of the fight, including the status of all actors.

        Returns:
            str: A string summarizing the fight's outcome and actors' statuses.
        """
        logger.info(f"")
        team_allies = self.team_a
        team_enemies = self.team_b

        def actor_status(actor: Actor) -> str:
            status = "Alive" if actor.health_points > 0 else "Dead"
            return f"{actor.name} - {status}, HP: {actor.health_points}"

        debrief = ["Fight Debrief:"]

        debrief.append("\nAllies Status:")
        for ally in team_allies:
            debrief.append(actor_status(ally))

        debrief.append("\nEnemies Status:")
        for enemy in team_enemies:
            debrief.append(actor_status(enemy))

        return "\n".join(debrief)

    def reset_combat(self):
        """
        Reset the combat state for all actors and the CombatManager.
        """
        for actor in self.team_a + self.team_b:
            actor.full_rest()
            actor.current_target = []
            actor.targeting_enemies = []
        self.has_initiative = False
        self.current_turn_index = 0
        self.turns_count = 0
        self.rounds_count = 0


def run_simulations(
    num_simulations: int,
    team_a: List[Actor],
    team_b: List[Actor],
    initiative_dc: int = 10,
):
    """
    Run a specified number of combat simulations between two teams and collect statistics.

    Parameters:
        num_simulations (int): The number of simulations to run.
        team_a (List[Actor]): List of actors in team A.
        team_b (List[Actor]): List of actors in team B.
        initiative_dc (int): Difficulty class for initiative rolls (default is 10).

    Returns:
        tuple: Containing lists of number of rounds, number of turns, win rate of team A, and remaining HP of actors.
    """
    num_rounds_list = []  # List to store the number of rounds for each simulation
    num_turns_list = []  # List to store the number of turns for each simulation
    winrate_A = 0  # Counter for wins by team A
    # List to store remaining HP of actors at the end of each simulation
    remaining_hp_list = []

    combat_manager = CombatManager(team_a, team_b, initiative_dc=initiative_dc)

    for _ in range(num_simulations):
        combat_manager.reset_combat()  # Reset the combat state for each simulation
        num_rounds, num_turns, winning_team, remaining_hp = combat_manager.run_combat()
        num_rounds_list.append(num_rounds)  # Collect the number of rounds
        num_turns_list.append(num_turns)  # Collect the number of turns
        if winning_team == "A":
            winrate_A += 1  # Increment win counter for team A if they won
        remaining_hp_list.append(remaining_hp)  # Collect the remaining HP of actors

    # Calculate the win rate for team A
    return (
        num_rounds_list,
        num_turns_list,
        winrate_A / num_simulations,
        remaining_hp_list,
    )


def plot_simulation_results(num_turns, win_rate, remaining_hp):
    """
    Plot the results of the combat simulations, including a histogram of number of turns,
    a pie chart of win rates, and a box plot of remaining HP.

    Parameters:
        num_turns (List[int]): List of the number of turns taken in each simulation.
        win_rate (float): Win rate of team A.
        remaining_hp (List[Dict[str, int]]): List of dictionaries containing remaining HP of actors.
    """
    # Histogram of Number of Turns
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.hist(
        num_turns,
        bins=20,
        edgecolor="black",
        histtype="bar",
    )
    plt.title("Number of Turns Distribution")
    plt.xlabel("Number of Turns")
    plt.ylabel("Frequency")

    # Win Rate Pie Chart
    plt.subplot(1, 3, 2)
    labels = "Team A Wins", "Team B Wins"
    sizes = [win_rate * 100, 100 - win_rate * 100]
    colors = ["lightblue", "lightcoral"]
    explode = (0.1, 0)  # explode the first slice (Team A)
    plt.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",  # Display percentage with one decimal place
        shadow=True,
        startangle=140,
    )
    plt.title("Win Rate")

    # Box Plot of Remaining HP
    plt.subplot(1, 3, 3)
    remaining_hp_flattened = {actor: [] for actor in remaining_hp[0].keys()}

    # Flatten the remaining HP data for box plot
    for battle in remaining_hp:
        for actor, hp in battle.items():
            remaining_hp_flattened[actor].append(hp)

    plt.boxplot(
        remaining_hp_flattened.values(), 0, "", labels=remaining_hp_flattened.keys()
    )
    plt.title("Remaining HP Distribution")
    plt.ylabel("HP")
    plt.xticks(rotation=90)

    # Adjust layout to prevent overlapping
    plt.tight_layout()
    plt.show()
