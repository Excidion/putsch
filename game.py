from entities import Player, Deck
from actions import Income, ForeignAid, Tax, Coup, Assassinate, Steal, Exchange
from actions import BlockableAction, CharacterAction, InterAction
from utils import (
    get_player_decision_Action,
    get_player_decision_ActionTarget,
    get_challenger,
    get_blocker,
    get_block_challenger,
)


def main(list_of_player_names):
    deck, players = setup_game(list_of_player_names)
    actions = [Income, ForeignAid, Tax, Coup, Assassinate, Steal, Exchange]

    # game loop
    while True:
        # 1 round loop
        for player in players:
            if not player.is_alive():
                continue

            elif len(get_alive_players(players)) == 1:
                print(f"{get_alive_players(players)[0]} wins!")
                return

            action_type = get_player_decision_Action(actions, player)
            action_kwargs = {"executing_player": player, "deck": deck}

            if InterAction in action_type.mro():
                target = get_player_decision_ActionTarget(
                    alive_players=get_alive_players(players),
                    executing_player=player,
                )
                action_kwargs["affected_player"] = target

            # init action object
            action = action_type(**action_kwargs)

            # eventual challenge of the action
            if isinstance(action, CharacterAction):
                challenger = get_challenger(
                    alive_players=get_alive_players(players),
                    executing_player=player,
                )
                if challenger is not None:
                    if action.challenge(challenging_player=challenger):
                        continue  # challenge succeeded, turn ends

            # eventual block of the action
            if isinstance(action, BlockableAction):
                blocker = get_blocker(
                    alive_players=get_alive_players(players),
                    executing_player=player,
                )
                if not blocker is None:
                    action.block(blocking_player=blocker)
                    # eventual challenge of the block
                    block_challenger = get_block_challenger(
                        alive_players=get_alive_players(players),
                        blocking_player=blocker,
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
    players = [Player(name) for name in list_of_player_names]
    for player in players:
        for card in deck.draw(initial_influences):
            player.add_card(card)
    return deck, players


def get_alive_players(players):
    return [p for p in players if p.is_alive()]


if __name__ == "__main__":
    main(list_of_player_names=[1, 2, 3, 4])
