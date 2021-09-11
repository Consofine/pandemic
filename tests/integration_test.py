import sys
sys.path.append('..')
import unittest
from board import *
from constants import *


class TestBoard:
    @classmethod
    def get_test_board(self):
        b = Board("somegameidhere", ["playeronesid", "playertwosid"])
        p = b.active_player
        p.add_card(CityCard("Atlanta"))
        p.add_card(CityCard("Chicago"))
        p.add_card(CityCard("Tokyo"))
        return b


class TestPlayer:
    @classmethod
    def get_test_player_one(self, cities: dict = TestBoard.get_test_board().cities):
        return Player("playeronesid", Role(), cities[STARTING_CITY])

    @classmethod
    def get_test_player_two(self, cities: dict = TestBoard.get_test_board().cities):
        return Player("playertwosid", Role(), cities[STARTING_CITY])


class TestAction:
    @classmethod
    def get_move_adjacent(self, to_city: Union[str, City]):
        return {"action": {"name": "MOVE_ADJACENT", "args": {"to_city": to_city}}}


if __name__ == "__main__":
    unittest.main()
