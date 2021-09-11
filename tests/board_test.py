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


class TestBoardMethods(unittest.TestCase):
    def test_board_init(self):
        b = TestBoard.get_test_board()
        self.assertEqual(len(b.cities.keys()), len(CITY_LIST.keys()))
        self.assertEqual(len(b.players), 2)
        self.assertEqual(b.active_player, TestPlayer.get_test_player_one())

    def test_set_active_player(self):
        b = TestBoard.get_test_board()
        p1 = TestPlayer.get_test_player_one()
        p2 = TestPlayer.get_test_player_two()
        self.assertEqual(b.active_player, p1)
        b.set_active_player(p2)
        self.assertNotEqual(b.active_player, p1)
        self.assertEqual(b.active_player, p2)

    def test_move_adjacent(self):
        """
        NOTE: this method doesn't decrement the player's action count. That's done
        in Board.take_action(). Don't check if the active player's action count has
        dropped after calling these helper methods, since they shouldn't be called
        directly except by take_action anyway.
        """
        b = TestBoard.get_test_board()
        self.assertTrue(b.move_adjacent(b.cities["Chicago"]))
        self.assertEqual(b.active_player.current_city, b.cities["Chicago"])
        self.assertFalse(b.move_adjacent(b.cities["Chicago"]))
        self.assertTrue(b.active_player.current_city,
                        b.cities["San Francisco"])

    def test_move_direct_flight(self):
        b = TestBoard.get_test_board()
        self.assertTrue(b.move_direct_flight(
            CityCard("Paris", CITY_LIST["Paris"])))
        self.assertEqual(b.active_player.current_city, b.cities["Paris"])
        self.assertEqual(
            b.players["playertwosid"].current_city, b.cities[STARTING_CITY])
        self.assertFalse(b.move_direct_flight(
            CityCard("Paris", CITY_LIST["Paris"])))

    def test_move_charter_flight(self):
        b = TestBoard.get_test_board()
        self.assertTrue(b.move_charter_flight(
            CityCard("Atlanta"), b.get_city("Chicago")))
        self.assertTrue(b.move_charter_flight(
            CityCard("Chicago"), b.get_city("Paris")))
        self.assertEqual(b.active_player.current_city, b.get_city("Paris"))
        self.assertFalse(b.move_charter_flight(
            CityCard("Beijing"), b.get_city("Tehran")))
        self.assertFalse(b.move_charter_flight(
            CityCard("Paris"), b.get_city("Algiers")))

    def test_move_shuttle_flight(self):
        b = TestBoard.get_test_board()
        self.assertTrue(b.get_city("Paris").add_research_station())
        self.assertTrue(b.move_shuttle_flight(b.get_city("Paris")))
        self.assertFalse(b.move_shuttle_flight(b.get_city("Algiers")))
        self.assertFalse(b.move_shuttle_flight(b.get_city("Paris")))
        self.assertEqual(b.active_player.current_city, b.get_city("Paris"))

    def test_build_research_station(self):
        b = TestBoard.get_test_board()
        self.assertTrue(b.move_adjacent(City("Chicago")))
        self.assertTrue(b.build_research_station())
        self.assertFalse(b.build_research_station())
        self.assertTrue(b.build_research_station("Tokyo"))

    def test_treat_disease(self):
        b = TestBoard.get_test_board()
        self.assertFalse(b.treat_disease("Potato Stew"))
        self.assertFalse(b.treat_disease(RED))
        b.active_player.current_city.add_single_disease(BLUE)
        self.assertTrue(b.treat_disease(BLUE))
        self.assertFalse(b.treat_disease(BLUE))
        self.assertEqual(b.active_player.current_city.disease_count[BLUE], 0)
        b.active_player.current_city.add_epidemic_disease(RED)
        b.active_player.current_city.add_epidemic_disease(BLUE)
        self.assertEqual(
            b.active_player.current_city.disease_count[RED], MAX_DISEASE_COUNT)
        p = b.active_player
        p.add_card(CityCard("New York"))
        p.add_card(CityCard("Madrid"))
        p.add_card(CityCard("London"))
        self.assertTrue(b.discover_cure(p.city_cards, BLUE))
        self.assertTrue(b.treat_disease(BLUE))
        self.assertEqual(p.current_city.disease_count[BLUE], 0)
        self.assertEqual(p.current_city.disease_count[RED], MAX_DISEASE_COUNT)

    def test_share_knowledge(self):
        b = TestBoard.get_test_board()
        p1 = b.get_player("playeronesid")
        p2 = b.get_player("playertwosid")
        p1.add_card(CityCard("Paris"))
        p2.add_card(CityCard("Algiers"))
        self.assertTrue(b.share_knowledge(CityCard("Paris"), p2, p1))
        self.assertFalse(b.share_knowledge(CityCard("Paris"), p2, p1))
        self.assertTrue(b.share_knowledge(CityCard("Algiers"), p1, p2))
        self.assertFalse(b.share_knowledge(CityCard("Algiers"), p1, p2))

    def test_discover_cure(self):
        b = TestBoard.get_test_board()
        p = b.active_player
        p.add_card(CityCard("Madrid"))
        p.add_card(CityCard("Milan"))
        p.add_card(CityCard("Essen"))
        self.assertFalse(b.disease_manager.is_cured(BLUE))
        self.assertTrue(b.discover_cure(p.city_cards, BLUE))
        self.assertFalse(b.discover_cure(p.city_cards, BLUE))
        self.assertFalse(b.discover_cure(p.city_cards, RED))
        self.assertEqual(len(p.city_cards), 1)


if __name__ == '__main__':
    unittest.main()
