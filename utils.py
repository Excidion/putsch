from random import choice, getrandbits, shuffle
from uuid import uuid4


def get_blocker(action, alive_players):
    blocker = choose_player_excluding(alive_players, action.executing_player)
    if blocker.controller.decide_block(action):
        return blocker
    else:
        return None


def get_block_challenger(action, alive_players):
    block_challenger = choose_player_excluding(alive_players, action.blocking_player)
    if block_challenger.controller.decide_challenge_block(action):
        return block_challenger
    else:
        return None


def get_challenger(action, alive_players):
    challenger = choose_player_excluding(alive_players, action.executing_player)
    if challenger.controller.decide_challenge(action):
        return challenger
    else:
        return None


def choose_player_excluding(players, excluded_player):
    options = get_relative_complement(players, excluded_player)
    return choice(options)


def get_relative_complement(complete_set, to_be_removed):
    return list(set(complete_set) - {to_be_removed})


def generate_id():
    return str(uuid4())


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
