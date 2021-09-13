from typing import Union
from controller import Controller, Serializer
from board import CityCard, Player, Board


class TestController(Controller):
    """
    Subclass with added methods for test purposes. Mostly just
    need this to be able to give players specific city cards, for
    example.
    """

    def give_card(self, game_id: str, card: CityCard, player: Union[str, Player] = None) -> bool:
        b: Board = Serializer.load_board(game_id)
        if not player:
            success = b.active_player.add_card(card)
        else:
            success = b.get_player(player).add_card(card)
        Serializer.save_board(b, game_id)
        return success

    def get_board_object(self, game_id: str) -> Board:
        """
        Get the actual board object. This is for testing use only.
        """
        b = Serializer.load_board(game_id)
        return b
