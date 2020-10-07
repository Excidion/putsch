from random import choice, sample, getrandbits, shuffle
from itertools import product


def get_player_decision_Action(actions, executing_player):
    available_actions = [a for a in actions if a.cost <= executing_player.coins]
    return choice(available_actions)


def get_player_decision_Exchange(cards, n):
    return sample(cards, k=n)


def get_player_decision_Reveal(influences):
    return choice(influences)


def get_blocker(alive_players, executing_player):
    return get_challenger(alive_players, executing_player)


def get_block_challenger(alive_players, blocking_player):
    return get_challenger(alive_players, blocking_player)


def get_challenger(alive_players, executing_player):
    challenger = get_player_decision_ActionTarget(alive_players, executing_player)
    return challenger if coinflip() else None


def get_player_decision_ActionTarget(alive_players, executing_player):
    potential_adversaries = set(alive_players) - {executing_player}
    return choice(list(potential_adversaries))


def coinflip():
    return bool(getrandbits(1))


def read_names():
    with open("names.txt") as f:
        return f.read().splitlines()


class RandomNameGenerator:
    names = read_names()
    shuffle(names)

    def get_random_name(self):
        try:
            return f"{self.names.pop(0)} {self.names.pop(0)}"
        except IndexError:
            return None
