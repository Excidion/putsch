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


def main(list_of_player_names):
    deck, players = setup_game(list_of_player_names)
    action_types = [Income, ForeignAid, Tax, Coup, Assassinate, Steal, Exchange]

    # game loop
    while True:
        # 1 round loop
        for player in players:
            if not player.is_alive():
                continue
            elif win_condition_met(players):
                return

            action_type = player.controller.choose_action(action_types)
            action_kwargs = {"executing_player": player, "deck": deck}

            if InterAction in action_type.mro():
                target = player.controller.choose_target(players)
                action_kwargs["target_player"] = target

            # init action object
            action = action_type(**action_kwargs)

            # eventual challenge of the action
            if isinstance(action, CharacterAction):
                challenger = get_challenger(
                    action=action, alive_players=get_alive_players(players),
                )
                if challenger is not None:
                    if action.challenge(challenging_player=challenger):
                        continue  # challenge succeeded, turn ends

            if win_condition_met(players):
                return  # last competitor might drop out after lost challenge

            # eventual block of the action
            if isinstance(action, BlockableAction):
                blocker = get_blocker(
                    action=action, alive_players=get_alive_players(players),
                )
                if not blocker is None:
                    action.block(blocking_player=blocker)
                    # eventual challenge of the block
                    block_challenger = get_block_challenger(
                        action=action, alive_players=get_alive_players(players),
                    )
                    if block_challenger is not None:
                        if not action.challenge_block(
                            block_challenging_player=block_challenger
                        ):
                            continue  # challenge failed, blocking worked, turn ends
                    else:
                        continue  # action blocked, turn ends

            # DO IT
            action.execute()


def setup_game(list_of_player_names, multiplicity=3, initial_influences=2):
    deck = Deck(multiplicity=multiplicity)
    players = []
    for name in list_of_player_names:
        players.append(Player(name=name, controller=get_random_AI()))
    for player in players:
        for card in deck.draw(initial_influences):
            player.add_card(card)
    return deck, players


def get_alive_players(players):
    return [p for p in players if p.is_alive()]


def win_condition_met(players):
    alive_players = get_alive_players(players)
    if len(alive_players) == 1:
        logging.info(f"{alive_players[0]} wins!")
        return True
    else:
        return False


if __name__ == "__main__":
    main(list_of_player_names=[1, 2, 3, 4])
