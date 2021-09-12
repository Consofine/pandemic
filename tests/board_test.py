import sys
sys.path.append('..')
import unittest
from board import *
from constants import *


class TestBoard:
    @classmethod
    def get_new_board(self):
        return Board(["playeronesid", "playertwosid", "playerthreesid"])

    @classmethod
    def get_test_board(self):
        b = Board(["playeronesid", "playertwosid"])
        p = b.active_player
        p.add_card(CityCard("Atlanta"))
        p.add_card(CityCard("Chicago"))
        p.add_card(CityCard("Tokyo"))
        p.add_card(CityCard("San Francisco"))
        return b

    @classmethod
    def get_curable_board(self):
        b = Board(["playeronesid", "playertwosid"])
        p = b.active_player
        p.add_card(CityCard("Atlanta"))
        p.add_card(CityCard("Chicago"))
        p.add_card(CityCard("Montreal"))
        p.add_card(CityCard("Essen"))
        p.add_card(CityCard("London"))
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
    def get_move_adjacent(self, to_city: str):
        return {"action": {"name": MOVE_ADJACENT, "args": {"to_city": to_city}}}

    @classmethod
    def get_move_direct_flight(self, city_card: str):
        return {"action": {"name": MOVE_DIRECT_FLIGHT, "args": {"city_card": city_card}}}

    @classmethod
    def get_move_charter_flight(self, city_card: str, to_city: str):
        return {"action": {"name": MOVE_CHARTER_FLIGHT, "args": {"city_card": city_card, "to_city": to_city}}}

    @classmethod
    def get_build_research_station(self, city_card: str):
        return {"action": {"name": BUILD_RESEARCH_STATION, "args": {"city_card": city_card}}}

    @classmethod
    def get_move_shuttle_flight(self, to_city: str):
        return {"action": {"name": MOVE_SHUTTLE_FLIGHT, "args": {"to_city": to_city}}}

    @classmethod
    def get_treat_disease(self, color: str):
        return {"action": {"name": TREAT_DISEASE, "args": {"color": color}}}


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
        self.assertTrue(b.move_adjacent(b.get_city("Chicago")))
        self.assertEqual(b.active_player.current_city, b.get_city("Chicago"))
        self.assertFalse(b.move_adjacent(b.get_city("Chicago")))
        self.assertTrue(b.move_adjacent(b.get_city("San Francisco")))

    def test_move_direct_flight(self):
        b = TestBoard.get_test_board()
        self.assertTrue(b.move_direct_flight(
            CityCard("Paris")))
        self.assertEqual(b.active_player.current_city, b.get_city("Paris"))
        self.assertEqual(
            b.get_player("playertwosid").current_city, b.get_city(STARTING_CITY))
        self.assertFalse(b.move_direct_flight(
            CityCard("Paris")))

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
        self.assertTrue(b.build_research_station(CityCard("Chicago")))
        self.assertFalse(b.build_research_station(CityCard("Chicago")))
        self.assertFalse(b.build_research_station(CityCard("Tokyo")))

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
        self.assertEqual(len(p.city_cards), 2)

    def test_move_to_next_player(self):
        b = TestBoard.get_test_board()
        self.assertEqual(b.active_player, b.get_player('playeronesid'))
        b.move_to_next_player()
        self.assertEqual(b.active_player, b.get_player('playertwosid'))
        b.move_to_next_player()
        self.assertEqual(b.active_player, b.get_player('playeronesid'))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS)

    def test_draw_city_cards(self):
        b = TestBoard.get_test_board()
        cards = b.draw_city_cards()
        while len(cards) == 2:
            cards = b.draw_city_cards()
        self.assertEqual(b.card_manager.infection_card_discard, [])
        self.assertEqual(
            len(b.card_manager.infection_card_deck), len(CITY_LIST.keys()))
        self.assertEqual(City.outbreaks_occurred, 0)
        if len(cards) == 1:
            self.assertEqual(b.infection_manager.rate, 2)
        elif not cards:
            self.assertEqual(b.infection_manager.rate, 3)

    def test_draw_infection_cards_and_place_cubes(self):
        b = TestBoard.get_test_board()
        b.draw_infection_cards_and_place_cubes()
        self.assertEqual(City.outbreaks_occurred, 0)
        self.assertEqual((DISEASE_CUBE_LIMIT * 4) -
                         sum(b.disease_manager.diseases_remaining.values()), 2)
        self.assertEqual(b.infection_manager.rate, 2)
        b.infection_manager.increase_level()
        b.infection_manager.increase_level()
        b.infection_manager.increase_level()
        self.assertEqual(b.infection_manager.rate, 3)
        b.draw_infection_cards_and_place_cubes()
        self.assertEqual((DISEASE_CUBE_LIMIT * 4) -
                         sum(b.disease_manager.diseases_remaining.values()), 5)

    def test_take_action_move_adjacent(self):
        b = TestBoard.get_new_board()
        self.assertTrue(b.take_action(TestAction.get_move_adjacent("Chicago")))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 1)
        self.assertEqual(b.active_player.current_city, b.get_city("Chicago"))
        self.assertFalse(b.take_action(
            TestAction.get_move_adjacent("Manila")))
        self.assertFalse(b.take_action(
            TestAction.get_move_adjacent("Hot Potato")))
        self.assertEqual(b.active_player.current_city, b.get_city("Chicago"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 1)
        self.assertTrue(b.take_action(
            TestAction.get_move_adjacent("Montreal")))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 2)
        self.assertEqual(b.active_player.current_city, b.get_city("Montreal"))
        self.assertTrue(b.take_action(
            TestAction.get_move_adjacent("New York")))
        self.assertTrue(b.take_action(TestAction.get_move_adjacent("London")))
        self.assertFalse(b.take_action(TestAction.get_move_adjacent("Essen")))

    def test_take_action_move_direct_flight(self):
        b = TestBoard.get_test_board()
        self.assertTrue(b.take_action(
            TestAction.get_move_direct_flight("Tokyo")))
        self.assertEqual(b.active_player.current_city, b.get_city("Tokyo"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 1)
        self.assertFalse(b.take_action(
            TestAction.get_move_direct_flight("Tokyo")))
        self.assertEqual(b.active_player.current_city, b.get_city("Tokyo"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 1)
        self.assertTrue(b.take_action(
            TestAction.get_move_direct_flight("Chicago")))
        self.assertEqual(b.active_player.current_city, b.get_city("Chicago"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 2)
        self.assertTrue(b.take_action(
            TestAction.get_move_direct_flight("Atlanta")))
        self.assertEqual(b.active_player.current_city, b.get_city("Atlanta"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 3)

    def test_take_action_move_charter_flight(self):
        b = TestBoard.get_test_board()
        self.assertTrue(b.take_action(
            TestAction.get_move_charter_flight("Atlanta", "Montreal")
        ))
        self.assertEqual(b.active_player.current_city, b.get_city("Montreal"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 1)
        self.assertTrue(b.take_action(
            TestAction.get_move_adjacent("Chicago")
        ))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 2)
        self.assertFalse(b.take_action(
            TestAction.get_move_charter_flight("Chicago", "Chicago")
        ))
        self.assertEqual(b.active_player.current_city, b.get_city("Chicago"))
        self.assertTrue(b.take_action(
            TestAction.get_move_charter_flight("Chicago", "Tehran")
        ))
        self.assertEqual(b.active_player.current_city, b.get_city("Tehran"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 3)
        self.assertFalse(b.take_action(
            TestAction.get_move_charter_flight("Chicago", "Tehran")
        ))
        self.assertEqual(b.active_player.current_city, b.get_city("Tehran"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 3)
        self.assertFalse(b.take_action(
            TestAction.get_move_charter_flight("Tehran", "Tokyo")
        ))
        self.assertTrue(b.take_action(
            TestAction.get_move_adjacent("Baghdad")
        ))
        self.assertEqual(b.active_player.current_city, b.get_city("Baghdad"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 4)

    def test_take_action_move_shuttle_flight(self):
        b = TestBoard.get_test_board()
        self.assertFalse(b.take_action(
            TestAction.get_move_shuttle_flight("Essen")))
        self.assertEqual(b.active_player.current_city, b.get_city("Atlanta"))
        self.assertTrue(b.take_action(TestAction.get_move_adjacent("Chicago")))
        self.assertFalse(b.take_action(
            TestAction.get_move_shuttle_flight("Tokyo")))
        self.assertTrue(b.take_action(
            TestAction.get_move_adjacent("San Francisco")))
        self.assertTrue(b.take_action(
            TestAction.get_build_research_station("San Francisco")))
        self.assertTrue(b.take_action(
            TestAction.get_move_shuttle_flight("Atlanta")))
        self.assertEqual(b.active_player.current_city, b.get_city("Atlanta"))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 4)

    def test_take_action_build_research_station(self):
        b = TestBoard.get_test_board()
        self.assertFalse(b.take_action(
            TestAction.get_build_research_station("Atlanta")))
        self.assertFalse(b.take_action(
            TestAction.get_build_research_station("Tehran")))
        self.assertTrue(b.take_action(TestAction.get_move_adjacent("Chicago")))
        self.assertTrue(b.take_action(
            TestAction.get_build_research_station("Chicago")))
        self.assertTrue(b.take_action(
            TestAction.get_move_adjacent("San Francisco")))
        self.assertFalse(b.take_action(
            TestAction.get_build_research_station("Karachi")))
        self.assertFalse(b.get_city("Karachi").has_research_station)
        self.assertTrue(b.take_action(
            TestAction.get_build_research_station("San Francisco")))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 4)
        self.assertEqual(len(b.active_player.city_cards), 2)

    def test_take_action_treat_disease(self):
        """
        NOTE: this ignores the DiseaseManager etc. Point isn't to test that
        functionality here, so I'm not gonna have this method change the disease
        counts and everything.
        """
        b = TestBoard.get_test_board()
        b.get_city("Atlanta").add_epidemic_disease(BLUE)
        b.get_city("Atlanta").add_single_disease(GREY)
        b.get_city("Chicago").add_epidemic_disease(RED)
        b.get_city("Chicago").add_single_disease(BLUE)
        b.get_city("San Francisco").add_single_disease(RED)
        b.get_city("San Francisco").add_single_disease(RED)
        self.assertTrue(b.take_action(TestAction.get_treat_disease(BLUE)))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 1)
        self.assertEqual(
            b.get_city(STARTING_CITY).disease_count[BLUE], MAX_DISEASE_COUNT - 1)
        self.assertEqual(b.get_city(STARTING_CITY).disease_count[GREY], 1)
        self.assertEqual(b.get_city(
            "Chicago").disease_count[RED], MAX_DISEASE_COUNT)
        self.assertEqual(b.get_city(
            "Chicago").disease_count[BLUE], 1)
        self.assertTrue(b.take_action(TestAction.get_move_adjacent("Chicago")))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 2)
        self.assertTrue(b.take_action(TestAction.get_treat_disease(BLUE)))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 3)
        self.assertEqual(b.get_city("Chicago").disease_count[BLUE], 0)
        self.assertEqual(b.get_city(
            "Chicago").disease_count[RED], MAX_DISEASE_COUNT)
        self.assertTrue(b.take_action(TestAction.get_treat_disease(RED)))
        self.assertEqual(b.active_player.actions_left, MAX_ACTIONS - 4)
        self.assertEqual(b.get_city(
            "Chicago").disease_count[RED], MAX_DISEASE_COUNT - 1)

        # MORE TESTS
        b = TestBoard.get_curable_board()
        b.get_city("Atlanta").add_epidemic_disease(BLUE)
        # also check that it doesn't trigger outbreak with different colors
        self.assertFalse(b.get_city("Atlanta").add_epidemic_disease(RED))
        self.assertTrue(b.discover_cure(b.active_player.city_cards, BLUE))
        self.assertTrue(b.take_action(TestAction.get_treat_disease(BLUE)))
        self.assertEqual(b.get_city("Atlanta").disease_count[BLUE], 0)
        self.assertTrue(b.take_action(TestAction.get_treat_disease(RED)))
        self.assertEqual(b.get_city(
            "Atlanta").disease_count[RED], MAX_DISEASE_COUNT - 1)


if __name__ == '__main__':
    unittest.main()
