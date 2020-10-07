from utils import get_player_decision_Exchange

# define base classes
class BaseAction:
    cost = 0

    def __init__(self, executing_player, deck, *args, **kwargs):
        self.executing_player = executing_player
        self.deck = deck
        self.executing_player.subtract_coins(self.cost)
        self.announce()

    def __str__(self):
        return self.__class__.__name__

    def announce(self):
        print(f"{self.executing_player} wants to execute {self}.")

    def announce_execute(self):
        print(f"{self.executing_player} executed {self}.")


class InterAction(BaseAction):
    def __init__(self, *args, affected_player, **kwargs):
        self.affected_player = affected_player
        super().__init__(*args, **kwargs)

    def announce(self):
        print(
            f"{self.executing_player} wants to execute {self} on {self.affected_player}."
        )

    def announce_execute(self):
        print(f"{self.executing_player} executed {self} on {self.affected_player}.")


class CharacterAction(BaseAction):
    def challenge(self, challenging_player):
        self.challenging_player = challenging_player
        print(f"{self.challenging_player} challenges {self.executing_player}'s {self}.")
        character = self.executing_player.challenge(self)
        if character is not None:
            print(f"{self.executing_player}'s {self} was not a bluff.")
            character.reveal()
            self.executing_player.remove_card(character)
            self.deck.put_back(character)
            self.executing_player.add_card(self.deck.draw())
            self.challenging_player.lose_influence()
            return False
        else:
            print(f"{self.executing_player}'s {self} was a bluff.")
            self.executing_player.lose_influence()
            return True


class BlockableAction(BaseAction):
    def block(self, blocking_player):
        self.blocking_player = blocking_player
        if isinstance(self, InterAction):
            print(
                f"{self.blocking_player} blocks {self.executing_player}'s attempt at {self} on {self.affected_player}."
            )

        else:
            print(
                f"{self.blocking_player} blocks {self.executing_player}'s attempt at {self}."
            )

    def challenge_block(self, block_challenging_player):
        self.block_challenging_player = block_challenging_player
        print(
            f"{self.block_challenging_player} challenges {self.blocking_player}'s block."
        )
        character = self.blocking_player.challenge(self, block=True)
        if character is not None:
            print(f"{self.blocking_player}'s block was not a bluff.")
            character.reveal()
            self.blocking_player.remove_card(character)
            self.deck.put_back(character)
            self.blocking_player.add_card(self.deck.draw())
            self.block_challenging_player.lose_influence()
            return False
        else:
            print(f"{self.blocking_player}'s block was a bluff.")
            self.blocking_player.lose_influence()
            return True


# From this line onwards the actually usable actions are defined
class Income(BaseAction):
    def execute(self):
        self.announce_execute()
        self.executing_player.add_coins(1)


class ForeignAid(BlockableAction):
    def execute(self):
        self.announce_execute()
        self.executing_player.add_coins(2)


class Tax(CharacterAction):
    def execute(self):
        self.announce_execute()
        self.executing_player.add_coins(3)


class Coup(InterAction):
    cost = 7

    def execute(self):
        super().announce_execute()
        self.affected_player.lose_influence()


class Assassinate(InterAction, BlockableAction, CharacterAction):
    cost = 3

    def execute(self):
        try:
            self.announce_execute()
            self.affected_player.lose_influence()
        except AssertionError:  # If the action was unsuccessfully challenged, the affected_player might have no influences left at the time of execution.
            print(
                f"{self.executing_player}'s {self} could not be executed, since {self.affected_player} is already out of the game."
            )


class Steal(InterAction, BlockableAction, CharacterAction):
    def execute(self):
        self.announce_execute()
        stolen_coins = 2
        while True:
            try:
                self.affected_player.subtract_coins(stolen_coins)
            except ValueError:  # player does not have enough coins
                stolen_coins -= 1
                continue  # try again
            break  # stealing was sucessfull
        self.executing_player.add_coins(stolen_coins)


class Exchange(CharacterAction):
    def execute(self):
        self.announce_execute()
        original = self.executing_player.get_unrevealed_influences()
        drawn = self.deck.draw(2)
        options = original + drawn
        choices = get_player_decision_Exchange(options, len(original))
        drops = set(original) - set(choices)
        gains = set(choices) - set(original)
        assert len(drops) == len(gains), f"Can't trade {len(drops)} for {len(gains)}."
        for drop in drops:
            self.executing_player.influences.remove(drop)
        for gain in gains:
            self.executing_player.influences.append(gain)
        unused = set(options) - set(choices)
        assert len(unused) == len(drawn)
        for card in unused:
            self.deck.put_back(card)