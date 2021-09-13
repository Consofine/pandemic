import sys
import unittest
sys.path.append('..')
from board import *
from constants import *
from controller import Controller
from test_controller import TestController

GAME_ID = "somegameidhere"
PLAYER_ONE_ID = "playeronesid"
PLAYER_TWO_ID = "playertwosid"


class ExampleController:
    @classmethod
    def get_test_controller(self) -> TestController:
        c = TestController()
        c.init_board(GAME_ID, [PLAYER_ONE_ID, PLAYER_TWO_ID])
        return c


"""
class TestBoard:
    @classmethod
    def get_test_board(self):
        b = Board("somegameidhere", ["playeronesid", "playertwosid"])
        p = c.get_board_object(GAME_ID).active_player
        p.add_card(CityCard("Atlanta"))
        p.add_card(CityCard("Chicago"))
        p.add_card(CityCard("Tokyo"))
        return b
"""


class TestAction:
    @classmethod
    def get_move_adjacent(self, to_city: str):
        return json.dumps({"action": {"name": MOVE_ADJACENT, "args": {"to_city": to_city}}})

    @classmethod
    def get_move_direct_flight(self, city_card: str):
        return json.dumps({"action": {"name": MOVE_DIRECT_FLIGHT, "args": {"city_card": city_card}}})

    @classmethod
    def get_move_charter_flight(self, city_card: str, to_city: str):
        return json.dumps({"action": {"name": MOVE_CHARTER_FLIGHT, "args": {"city_card": city_card, "to_city": to_city}}})

    @classmethod
    def get_build_research_station(self, city_card: str):
        return json.dumps({"action": {"name": BUILD_RESEARCH_STATION, "args": {"city_card": city_card}}})

    @classmethod
    def get_move_shuttle_flight(self, to_city: str):
        return json.dumps({"action": {"name": MOVE_SHUTTLE_FLIGHT, "args": {"to_city": to_city}}})

    @classmethod
    def get_treat_disease(self, color: str):
        return json.dumps({"action": {"name": TREAT_DISEASE, "args": {"color": color}}})

    @classmethod
    def get_share_knowledge(self, city_card: str, player_to: str, player_from: str):
        return json.dumps({"action": {"name": SHARE_KNOWLEDGE, "args": {"city_card": city_card, "player_to": player_to, "player_from": player_from}}})

    @classmethod
    def get_discover_cure(self, city_cards: List[str], color: str):
        return json.dumps({"action": {"name": DISCOVER_CURE, "args": {"city_cards": city_cards, "color": color}}})


class TestActionsAndAbilities(unittest.TestCase):
    def assertOkay(self, msg):
        assert not json.loads(msg)["error"]

    def assertNotOkay(self, msg):
        assert json.loads(msg)["error"]

    def test_take_action_move_adjacent(self):
        c: TestController = ExampleController.get_test_controller()
        self.assertOkay(c.handle_input(
            GAME_ID, TestAction.get_move_adjacent("Chicago")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 1)
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(
            GAME_ID).get_city("Chicago"))
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_adjacent("Manila")))
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_adjacent("Hot Potato")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(
            GAME_ID).get_city("Chicago"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 1)
        self.assertOkay(c.handle_input(
            GAME_ID, TestAction.get_move_adjacent("Montreal")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 2)
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(
            GAME_ID).get_city("Montreal"))
        self.assertOkay(c.handle_input(
            GAME_ID, TestAction.get_move_adjacent("New York")))
        self.assertOkay(c.handle_input(
            GAME_ID, TestAction.get_move_adjacent("London")))
        self.assertNotOkay(c.handle_input(
            GAME_ID, TestAction.get_move_adjacent("Essen")))

    def test_take_action_move_direct_flight(self):
        c: TestController = ExampleController.get_test_controller()
        self.assertTrue(c.give_card(GAME_ID, CityCard("Tokyo")))
        self.assertTrue(c.give_card(GAME_ID, CityCard("Chicago")))
        self.assertTrue(c.give_card(GAME_ID, CityCard("Atlanta")))
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_direct_flight("Tokyo")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Tokyo"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 1)
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_direct_flight("Tokyo")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Tokyo"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 1)
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_direct_flight("Chicago")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Chicago"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 2)
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_direct_flight("Atlanta")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Atlanta"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 3)

    def test_take_action_move_charter_flight(self):
        c: TestController = ExampleController.get_test_controller()
        self.assertTrue(c.give_card(GAME_ID, CityCard("Atlanta")))
        self.assertTrue(c.give_card(GAME_ID, CityCard("Chicago")))
        self.assertOkay(c.handle_input(
            GAME_ID, TestAction.get_move_charter_flight("Atlanta", "Montreal")))
        self.assertEqual(c.get_board_object(GAME_ID).active_player.current_city,
                         c.get_board_object(GAME_ID).get_city("Montreal"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 1)
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_adjacent(
                                           "Chicago")
                                       ))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 2)
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_charter_flight(
                                              "Chicago", "Chicago")
                                          ))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Chicago"))
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_charter_flight(
                                           "Chicago", "Tehran")
                                       ))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Tehran"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 3)
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_charter_flight(
                                              "Chicago", "Tehran")
                                          ))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Tehran"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 3)
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_charter_flight(
                                              "Tehran", "Tokyo")
                                          ))
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_adjacent(
                                           "Baghdad")
                                       ))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Baghdad"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 4)

    def test_take_action_move_shuttle_flight(self):
        c: TestController = ExampleController.get_test_controller()
        self.assertTrue(c.give_card(GAME_ID, CityCard("San Francisco")))
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_shuttle_flight("Essen")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Atlanta"))
        self.assertOkay(c.handle_input(
            GAME_ID, TestAction.get_move_adjacent("Chicago")))
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_move_shuttle_flight("Tokyo")))
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_adjacent("San Francisco")))
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_build_research_station("San Francisco")))
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_shuttle_flight("Atlanta")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.current_city, c.get_board_object(GAME_ID).get_city("Atlanta"))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 4)

    def test_take_action_build_research_station(self):
        c: TestController = ExampleController.get_test_controller()
        self.assertTrue(c.give_card(GAME_ID, CityCard("Chicago")))
        self.assertTrue(c.give_card(GAME_ID, CityCard("San Francisco")))
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_build_research_station("Atlanta")))
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_build_research_station("Tehran")))
        self.assertOkay(c.handle_input(
            GAME_ID, TestAction.get_move_adjacent("Chicago")))

        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_build_research_station("Chicago")))
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_move_adjacent("San Francisco")))
        self.assertNotOkay(c.handle_input(GAME_ID,
                                          TestAction.get_build_research_station("Karachi")))
        self.assertFalse(c.get_board_object(
            GAME_ID).get_city("Karachi").has_research_station)
        self.assertOkay(c.handle_input(GAME_ID,
                                       TestAction.get_build_research_station("San Francisco")))
        self.assertEqual(c.get_board_object(
            GAME_ID).active_player.actions_left, MAX_ACTIONS - 4)
        self.assertEqual(len(c.get_board_object(
            GAME_ID).active_player.city_cards), 2)

    # def test_take_action_treat_disease(self):
    #     """
    #     NOTE: this ignores the DiseaseManager etc. Point isn't to test that
    #     functionality here, so I'm not gonna have this method change the disease
    #     counts and everything.
    #     """
    #     c = TestController.get_test_controller()
    #     b = c.get_board_object(GAME_ID)
    #     c.get_board_object(GAME_ID).get_city("Atlanta").add_epidemic_disease(BLUE)
    #     c.get_board_object(GAME_ID).get_city("Atlanta").add_single_disease(GREY)
    #     c.get_board_object(GAME_ID).get_city("Chicago").add_epidemic_disease(RED)
    #     c.get_board_object(GAME_ID).get_city("Chicago").add_single_disease(BLUE)
    #     c.get_board_object(GAME_ID).get_city("San Francisco").add_single_disease(RED)
    #     c.get_board_object(GAME_ID).get_city("San Francisco").add_single_disease(RED)
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_treat_disease(BLUE)))
    #     self.assertEqual(c.get_board_object(GAME_ID).active_player.actions_left, MAX_ACTIONS - 1)
    #     self.assertEqual(
    #         c.get_board_object(GAME_ID).get_city(STARTING_CITY).disease_count[BLUE], MAX_DISEASE_COUNT - 1)
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city(STARTING_CITY).disease_count[GREY], 1)
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city(
    #         "Chicago").disease_count[RED], MAX_DISEASE_COUNT)
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city(
    #         "Chicago").disease_count[BLUE], 1)
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_move_adjacent("Chicago")))
    #     self.assertEqual(c.get_board_object(GAME_ID).active_player.actions_left, MAX_ACTIONS - 2)
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_treat_disease(BLUE)))
    #     self.assertEqual(c.get_board_object(GAME_ID).active_player.actions_left, MAX_ACTIONS - 3)
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city("Chicago").disease_count[BLUE], 0)
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city(
    #         "Chicago").disease_count[RED], MAX_DISEASE_COUNT)
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_treat_disease(RED)))
    #     self.assertEqual(c.get_board_object(GAME_ID).active_player.actions_left, MAX_ACTIONS - 4)
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city(
    #         "Chicago").disease_count[RED], MAX_DISEASE_COUNT - 1)

    #     # MORE TESTS
    #     """
    #     b = TestBoard.get_curable_board()
    #     c.get_board_object(GAME_ID).get_city("Atlanta").add_epidemic_disease(BLUE)
    #     # also check that it doesn't trigger outbreak with different colors
    #     self.assertFalse(c.get_board_object(GAME_ID).get_city("Atlanta").add_epidemic_disease(RED))
    #     self.assertTrue(c.get_board_object(GAME_ID).discover_cure(c.get_board_object(GAME_ID).active_player.city_cards, BLUE))
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_treat_disease(BLUE)))
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city("Atlanta").disease_count[BLUE], 0)
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_treat_disease(RED)))
    #     self.assertEqual(c.get_board_object(GAME_ID).get_city(
    #         "Atlanta").disease_count[RED], MAX_DISEASE_COUNT - 1)
    #     """

    # def test_take_action_share_knowledge(self):
    #     c = TestController.get_test_controller()
    #     b = c.get_board_object(GAME_ID)
    #     self.assertTrue(json.loads(c.handle_input(GAME_ID, TestAction.get_share_knowledge(
    #         "Atlanta", "playertwosid", "playeronesid")))
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_share_knowledge(
    #         "Chicago", "playertwosid", "playeronesid")))
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_share_knowledge(
    #         "Tokyo", "playertwosid", "playeronesid")))
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_share_knowledge(
    #         "San Francisco", "playeronesid", "playertwosid")))
    #     self.assertEqual(c.get_board_object(GAME_ID).active_player.actions_left, MAX_ACTIONS - 1)
    #     self.assertTrue(CityCard("Atlanta") not in c.get_board_object(GAME_ID).get_player(
    #         "playeronesid").city_cards)
    #     self.assertTrue(CityCard("Atlanta") in c.get_board_object(GAME_ID).get_player(
    #         "playertwosid").city_cards)
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_move_adjacent("Chicago")))
    #     c.get_board_object(GAME_ID).set_active_player(c.get_board_object(GAME_ID).get_player("playertwosid"))
    #     self.assertTrue(json.loads(c.handle_input(
    #         GAME_ID, TestAction.get_move_adjacent("Chicago")))
    #     self.assertTrue(json.loads(c.handle_input(GAME_ID, TestAction.get_share_knowledge(
    #         "Chicago", "playertwosid", "playeronesid")))
    #     self.assertTrue(CityCard("Chicago") not in c.get_board_object(GAME_ID).get_player(
    #         "playeronesid").city_cards)

    # def test_take_action_discover_cure(self):
    #     """
    #     b = TestBoard.get_curable_board()
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_discover_cure(
    #         ["Atlanta", "Chicago", "Montreal", "Essen", "London"], RED)))
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_discover_cure(
    #         ["Atlanta", "Chicago", "Montreal", "Tokyo", "London"], BLUE)))
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_discover_cure(
    #         ["Tokyo", "Beijing", "Shanghai", "Jakarta", "Sydney"], BLUE)))
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_discover_cure(
    #         ["Tokyo", "Beijing", "Shanghai", "Jakarta", "Sydney"], RED)))
    #     self.assertTrue(json.loads(c.handle_input(GAME_ID, TestAction.get_discover_cure(
    #         ["Atlanta", "Chicago", "Montreal", "Essen", "London"], BLUE)))
    #     self.assertFalse(json.loads(c.handle_input(GAME_ID, TestAction.get_discover_cure(
    #         ["Atlanta", "Chicago", "Montreal", "Essen", "London"], BLUE)))
    #     self.assertEqual(len(c.get_board_object(GAME_ID).active_player.city_cards), 0)
    #     self.assertTrue(c.get_board_object(GAME_ID).disease_manager.diseases_cured[BLUE])
    #     self.assertFalse(c.get_board_object(GAME_ID).disease_manager.diseases_cured[RED])
    #     """


if __name__ == "__main__":
    unittest.main()
