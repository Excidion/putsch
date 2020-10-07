from random import shuffle
from characters import Ambassador, Assassin, Captain, Contessa, Duke
from utils import get_player_decision_Reveal


class Player:
    def __init__(self, name=None, initial_coins=2):
        self.name = name
        self.influences = []
        self.coins = initial_coins

    def __str__(self):
        if self.name is None:
            return "An anonymous player"
        else:
            return f"Player {self.name}"

    def is_alive(self):
        return not all(i.revealed for i in self.influences)

    def add_coins(self, n):
        assert isinstance(n, int)
        assert n >= 0
        self.coins += n

    def subtract_coins(self, n):
        assert isinstance(n, int)
        assert n >= 0
        if self.coins >= n:
            self.coins -= n
        else:
            raise ValueError(
                f"{self} has insufficient coins. {n} needed but only {self.coins} available."
            )

    def lose_influence(self):
        assert self.is_alive(), f"{self} has no influences left."
        print(f"{self} loses 1 influence.")
        character = get_player_decision_Reveal(self.get_unrevealed_influences())
        i = self.influences.index(character)
        self.influences[i].reveal()
        if not self.is_alive():
            print(f"{self} is out of the game.")

    def get_unrevealed_influences(self):
        return [i for i in self.influences if not i.revealed]

    def add_card(self, character):
        self.influences.append(character)

    def remove_card(self, character):
        self.influences.remove(character)

    def challenge(self, action, block=False):
        for character in self.get_unrevealed_influences():
            if (
                (type(action) in character.actions)
                if not block
                else (type(action) in character.blocks)
            ):
                return character  # character that can perform the action/block
        else:
            return None  # admit bluff


class Deck:
    def __init__(self, characters=None, multiplicity=3):
        self.characters = characters or {
            Ambassador,
            Assassin,
            Captain,
            Contessa,
            Duke,
        }  # on default (characters = None) use predefined set
        self.cards = [c() for c in list(self.characters) * multiplicity]
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def draw(self, n=1):
        assert isinstance(n, int)
        assert n > 0
        if n == 1:
            return self.cards.pop(0)
        elif n <= len(self.cards):
            return [self.cards.pop(0) for i in range(n)]
        else:
            raise ValueError(f"Not enough cards in deck to draw {n}")

    def put_back(self, character):
        self.cards.append(character)
        self.shuffle()
