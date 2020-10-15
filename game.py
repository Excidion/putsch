from entities import Player, Deck, get_random_AI
from actions import Income, ForeignAid, Tax, Coup, Assassinate, Steal, Exchange
from actions import BlockableAction, CharacterAction, InterAction
from utils import get_challenger, get_blocker, get_block_challenger
import logging

logging.basicConfig(
    filename="events.log",
    level=logging.DEBUG,
    format=r"%(asctime)s, %(levelname)s, %(message)s",
    filemode="w",
)


class GameOver(BaseException):
    pass


class Game:
    def __init__(
        self, players, deck, n_influences=2, starting_coins=2, action_types=None
    ):
        # base setup
        self.players = players
        self.deck = deck
        self.action_types = action_types or [
            Income,
            ForeignAid,
            Tax,
            Coup,
            Assassinate,
            Steal,
            Exchange,
        ]
        self.n_influences = n_influences
        self.distribute_cards()
        self.distribute_coins(starting_coins)
        # track game state
        self.actions = []

    def distribute_cards(self):
        for player in self.players:
            for i in range(self.n_influences):
                player.add_card(self.deck.draw())

    def distribute_coins(self, starting_coins):
        for player in self.players:
            player.coins = starting_coins

    def win_condition_met(self):
        alive_players = self.get_alive_players()
        if len(alive_players) == 1:
            return True
        else:
            return False

    def get_alive_players(self):
        return [p for p in self.players if p.is_alive()]

    def run(self):
        while not self.win_condition_met():
            try:
                self.run_round()
            except GameOver:
                logging.info(f"{self.get_alive_players()[0]} wins!")
                return

    def run_round(self):
        for player in self.players:
            if self.win_condition_met():
                raise GameOver
            elif not player.is_alive():
                continue
            else:
                self.run_turn(player)

    def run_turn(self, player):
        action_type = player.controller.choose_action(self.action_types)
        action_kwargs = {"executing_player": player, "deck": self.deck}

        if InterAction in action_type.mro():
            target = player.controller.choose_target(self.players)
            action_kwargs["target_player"] = target

        # init action object
        action = action_type(**action_kwargs)
        self.actions.append(action)

        # eventual challenge of the action
        if isinstance(action, CharacterAction):
            challenger = get_challenger(
                action=action,
                alive_players=self.get_alive_players(),
            )
            if challenger is not None:
                if action.challenge(challenging_player=challenger):
                    return  # challenge succeeded, turn ends

        if self.win_condition_met():
            raise GameOver  # last competitor might drop out after lost challenge

        # eventual block of the action
        if isinstance(action, BlockableAction):
            blocker = get_blocker(
                action=action,
                alive_players=self.get_alive_players(),
            )
            if not blocker is None:
                action.block(blocking_player=blocker)
                # eventual challenge of the block
                block_challenger = get_block_challenger(
                    action=action,
                    alive_players=self.get_alive_players(),
                )
                if block_challenger is not None:
                    if not action.challenge_block(
                        block_challenging_player=block_challenger
                    ):
                        return  # challenge failed, blocking worked, turn ends
                else:
                    return  # action blocked, turn ends

        # DO IT
        action.execute()


def main(list_of_player_names):
    deck = Deck()
    players = [Player(get_random_AI(), name) for name in list_of_player_names]
    game = Game(players, deck)
    game.run()


if __name__ == "__main__":
    main(list_of_player_names=[1, 2, 3, 4])
