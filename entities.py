from random import shuffle, choice, sample
from characters import Ambassador, Assassin, Captain, Contessa, Duke
from actions import Coup, InterAction
from utils import coinflip, generate_id
import logging


class Player:
    def __init__(self, controller=None, name=None, coins=2, influences=None):
        self.controller = controller
        self.name = name
        self.influences = influences or []
        self.coins = coins
        if self.controller is not None:
            self.controller.connect_player(self)

    def __repr__(self):
        return f"{self.__class__.__name__}(controller={repr(self.controller)}, name='{self.name}', coins={self.coins}, influences={self.influences})"

    def __str__(self):
        if self.name is None:
            return f"An anonymous {self.__class__.__name__}"
        else:
            return f"{self.__class__.__name__} {self.name}"

    def connect_controller(self, controller):
        """
        Sets the player's controller-attribute and makes sure, that the controller's player-attribute is matching.
        The 'connect_player' method is exectued and mirros this behavior on the controller side.
        The recursion is broken via AssertionError once both attributes are set.
        If both attributes are matchingly set, the Error is not re-raised.
        """
        assert self.controller is None, f"{self} is connected to {self.controller}"
        self.controller = controller
        try:
            controller.connect_player(self)
        except AssertionError:  # either connection established or not possible
            if controller.player is not self:  # not possible
                self.controller = None  # reset player-side
                raise

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
        logging.info(f"{self} loses 1 influence.")
        character = self.controller.choose_reveal(self.get_unrevealed_influences())
        character.reveal()
        if not self.is_alive():
            logging.info(f"{self} is out of the game.")

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


class BaseController:
    def __init__(self):
        self.id = generate_id()
        self.player = None

    def __str__(self):
        name = self.__class__.__name__
        if "AI" in name:
            return f"{name.split('_')[1]} AI"
        else:
            return f"{name} {self.id}"

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def connect_player(self, player):
        """
        Sets the controller's player-attribute and makes sure, that the player's controller attribute is matching.
        The 'connect_controller' method is exectued and mirros this behavior on the player side.
        The recursion is broken via AssertionError once both attributes are set.
        If both attributes are matchingly set, the Error is not re-raised.
        """
        assert self.player is None, f"{self} is connected to {self.player}"
        self.player = player
        try:
            player.connect_controller(self)
        except AssertionError:  # either connection established or not possible
            if player.controller is not self:  # not possible
                self.player = None  # reset controller-side
                raise

    def get_available_actions(self, action_types):
        budget = self.player.coins
        if budget < 10:
            return [a for a in action_types if a.cost <= budget]
        else:
            return [Coup]


class AIController_Random(BaseController):
    def choose_action(self, action_types):
        options = self.get_available_actions(action_types)
        return choice(options)

    def choose_target(self, players):
        alive_players = [p for p in players if p.is_alive()]
        competitors = list(set(alive_players) - {self.player})
        return choice(competitors)

    def choose_exchange(self, cards, n):
        return sample(cards, n)

    def choose_reveal(self, influences):
        return choice(influences)

    def decide_challenge(self, action):
        return coinflip()

    def decide_block(self, action):
        return coinflip()

    def decide_challenge_block(self, action):
        return coinflip()


class AIController_Defensive(AIController_Random):
    def choose_action(self, action_types):
        options = self.get_available_actions(action_types)
        peaceful_options = [o for o in options if InterAction not in o.mro()]
        if len(peaceful_options) > 0:
            return choice(peaceful_options)
        else:
            return choice(options)

    def decide_challenge(self, action):
        return False

    def decide_block(self, action):
        if isinstance(action, InterAction):
            return action.target_player is self.player
        else:
            return False

    def decide_challenge_block(self, action):
        return False


class AIController_Offensive(AIController_Random):
    def choose_action(self, action_types):
        options = self.get_available_actions(action_types)
        options = [o for o in options if InterAction in o.mro()]
        return choice(options)

    def decide_challenge(self, action):
        if isinstance(action, InterAction):
            return action.target_player is self.player
        else:
            return False

    def decide_challenge_block(self, action):
        return action.executing_player is self.player


class AIController_Gullible(AIController_Random):
    def decide_challenge(self, action):
        return False

    def decide_challenge_block(self, action):
        return False


class AIController_Skeptic(AIController_Random):
    def decide_challenge(self, action):
        return True

    def decide_challenge_block(self, action):
        return True


class AIController_Opressor(AIController_Random):
    def choose_target(self, players):
        alive_players = [p for p in players if p.is_alive()]
        competitors = list(set(alive_players) - {self.player})
        targets = self.choose_weakest(competitors)
        return choice(targets)

    def choose_weakest(self, competitors):
        min_i = min([len(c.get_unrevealed_influences()) for c in competitors])
        targets = [
            c for c in competitors if len(c.get_unrevealed_influences()) == min_i
        ]
        min_c = min([t.coins for t in targets])
        targets = [t for t in targets if t.coins == min_c]
        return targets


class AIController_Revolutionary(AIController_Random):
    def choose_target(self, players):
        alive_players = [p for p in players if p.is_alive()]
        competitors = list(set(alive_players) - {self.player})
        targets = self.choose_strongest(competitors)
        return choice(targets)

    def choose_strongest(self, competitors):
        max_i = max([len(c.get_unrevealed_influences()) for c in competitors])
        targets = [
            c for c in competitors if len(c.get_unrevealed_influences()) == max_i
        ]
        max_c = max([t.coins for t in targets])
        targets = [t for t in targets if t.coins == max_c]
        return targets


def get_random_AI():
    AIs = [
        AIController_Random,
        AIController_Defensive,
        AIController_Offensive,
        AIController_Gullible,
        AIController_Skeptic,
        AIController_Opressor,
        AIController_Revolutionary,
    ]
    return choice(AIs)()


class HumanController(BaseController):
    pass  # TODO communicate with some sort of UI
