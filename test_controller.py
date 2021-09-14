from typing import Union, List
from controller import Controller, Serializer
from board import CityCard, Player, Board


class TestController(Controller):
    """
    Subclass with added methods for test purposes. Mostly just
    need this to be able to give players specific city cards, for
    example.
    """

    def init_board(self, game_id: str, player_ids: List[str], starting_city: str = None) -> str:
        """
        Save the game_id with this object so we don't need to supply the 
        game id to all the test methods in integration_tests
        """
        self.game_id = game_id
        return super().init_board(game_id, player_ids, starting_city)

    def give_card(self, card: CityCard, player: Union[str, Player] = None) -> bool:
        """
        Add the given city card to a player's hand.
        """
        b: Board = Serializer.load_board(self.game_id)
        if not player:
            success = b.active_player.add_card(card)
        else:
            success = b.get_player(player).add_card(card)
        Serializer.save_board(b, self.game_id)
        return success

    def add_single_disease(self, city_name: str, color: str) -> bool:
        """
        Add a disease of the given color onto the given city.
        """
        b: Board = Serializer.load_board(self.game_id)
        wasOutbreak = b.cities[city_name].add_single_disease(b.cities, color)
        Serializer.save_board(b, self.game_id)
        return wasOutbreak

    def add_epidemic_disease(self, city_name: str, color: str) -> bool:
        """
        Add an epidemic disease of the given color onto the given city.
        """
        b: Board = Serializer.load_board(self.game_id)
        wasOutbreak = b.cities[city_name].add_epidemic_disease(b.cities, color)
        Serializer.save_board(b, self.game_id)
        return wasOutbreak

    def get_board_object(self) -> Board:
        """
        Get the actual board object.
        """
        b = Serializer.load_board(self.game_id)
        return b

    def set_active_player(self, player_id: str) -> None:
        """
        Set active player to whoever is passed along
        """
        b: Board = Serializer.load_board(self.game_id)
        b.set_active_player(b.get_player(player_id))
        Serializer.save_board(b, self.game_id)
