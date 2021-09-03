import sys
sys.path.append('..')
import unittest
from board import *
from custom_exceptions import GameEndedError
from constants import *


class TestMap():
    def __init__(self):
        self.cities = Board.init_cities()

    def get_city(self, city_name: str) -> City:
        return self.cities[city_name]


class TestPlayer:
    @classmethod
    def get_test_player(self):
        cities: dict = Board.init_cities()
        return Player("someidhere", Role(), cities[STARTING_CITY])


class TestCityCardDeck:
    def __init__(self):
        self.sf = CityCard("San Francisco", BLUE)
        self.la = CityCard("Los Angeles", YELLOW)
        self.chi = CityCard("Chicago", BLUE)
        self.mc = CityCard("Mexico City", YELLOW)


class TestInfectionCardDeck:
    def __init__(self):
        self.sf = InfectionCard("San Francisco", BLUE)
        self.la = InfectionCard("Los Angeles", YELLOW)
        self.chi = InfectionCard("Chicago", BLUE)
        self.mc = InfectionCard("Mexico City", YELLOW)


class TestCityMethods(unittest.TestCase):
    def test_city_init(self):
        test_sf = TestMap().get_city("San Francisco")
        self.assertEqual(test_sf.name, "San Francisco")
        self.assertEqual(test_sf.color, BLUE)
        self.assertFalse(test_sf.has_research_station)

    def test_eq(self):
        test_sf = TestMap().get_city("San Francisco")
        self.assertEqual(test_sf, CityCard("San Francisco", BLUE))
        self.assertNotEqual(test_sf, CityCard("San Francisco", YELLOW))
        self.assertNotEqual(test_sf, CityCard("Tokyo", RED))

    def test_add_disease(self):
        test_map = TestMap()
        self.assertFalse(test_map.get_city(
            "Los Angeles").add_single_disease(BLUE))
        self.assertFalse(test_map.get_city(
            "San Francisco").add_single_disease(YELLOW))
        self.assertFalse(test_map.get_city(
            "San Francisco").add_single_disease(YELLOW))
        self.assertFalse(test_map.get_city(
            "San Francisco").add_single_disease(YELLOW))
        self.assertTrue(test_map.get_city(
            "San Francisco").add_single_disease(YELLOW))
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[YELLOW], 3)
        self.assertEqual(test_map.get_city("Chicago").disease_count[YELLOW], 1)
        self.assertEqual(test_map.get_city(
            "Los Angeles").disease_count[YELLOW], 1)
        self.assertEqual(test_map.get_city(
            "Los Angeles").disease_count[BLUE], 1)
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[YELLOW], 0)

    def test_trigger_outbreak(self):
        test_map = TestMap()
        test_map.get_city("San Francisco").trigger_outbreak(YELLOW, [])
        test_map.get_city("Los Angeles").trigger_outbreak(
            YELLOW, [test_map.get_city("Mexico City")])
        self.assertEqual(test_map.get_city("Chicago").disease_count[YELLOW], 2)
        self.assertEqual(test_map.get_city(
            "Los Angeles").disease_count[YELLOW], 1)
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[BLUE], 0)
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[YELLOW], 0)

        test_map.get_city("Chicago").trigger_outbreak(BLUE, [])
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[BLUE], 1)
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[BLUE], 1)
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[YELLOW], 1)

    def test_add_epidemic_disease(self):
        test_map = TestMap()
        self.assertFalse(test_map.get_city(
            "Chicago").add_epidemic_disease(BLUE))
        self.assertEqual(test_map.get_city("Chicago").disease_count[BLUE], 3)
        self.assertFalse(test_map.get_city(
            "Chicago").add_epidemic_disease(YELLOW))
        self.assertEqual(test_map.get_city("Chicago").disease_count[YELLOW], 3)
        self.assertEqual(test_map.get_city("Chicago").disease_count[RED], 0)
        self.assertEqual(test_map.get_city("Chicago").disease_count[GREY], 0)
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[YELLOW], 0)
        self.assertTrue(test_map.get_city(
            "Chicago").add_epidemic_disease(YELLOW))
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[YELLOW], 1)
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[YELLOW], 1)
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[BLUE], 0)

    def test_treat_single_disease(self):
        test_map = TestMap()
        self.assertFalse(test_map.get_city(
            "Chicago").treat_single_disease(BLUE))
        self.assertFalse(test_map.get_city(
            "Chicago").add_epidemic_disease(BLUE))
        self.assertTrue(test_map.get_city(
            "Chicago").treat_single_disease(BLUE))
        self.assertEqual(test_map.get_city("Chicago").disease_count[BLUE], 2)
        self.assertFalse(test_map.get_city(
            "Chicago").treat_single_disease(YELLOW))

    def test_treat_all_disease(self):
        test_map = TestMap()
        test_map.get_city("San Francisco").add_epidemic_disease(BLUE)
        self.assertTrue(test_map.get_city(
            "San Francisco").treat_all_disease(BLUE))
        self.assertFalse(test_map.get_city(
            "San Francisco").treat_all_disease(BLUE))
        self.assertFalse(test_map.get_city(
            "San Francisco").treat_all_disease(YELLOW))
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[BLUE], 0)

    def test_add_research_station(self):
        test_map = TestMap()
        self.assertTrue(test_map.get_city(
            "San Francisco").add_research_station())
        self.assertFalse(test_map.get_city(
            "San Francisco").add_research_station())


class TestInfectionManagerMethods(unittest.TestCase):
    def test_infection_manager_init(self):
        infection_manager = InfectionManager()
        self.assertEqual(infection_manager.level, 1)
        self.assertEqual(infection_manager.rate, 2)

    def test_infection_manager_increase_level(self):
        infection_manager = InfectionManager()
        self.assertEqual(infection_manager.level, 1)
        self.assertEqual(infection_manager.rate, 2)
        infection_manager.increase_level()
        self.assertEqual(infection_manager.level, 2)
        self.assertEqual(infection_manager.rate, 2)
        infection_manager.increase_level()
        infection_manager.increase_level()
        self.assertEqual(infection_manager.rate, 3)
        self.assertEqual(infection_manager.level, 4)


class TestDiseaseStateMethods(unittest.TestCase):
    def test_init(self):
        disease_manager = DiseaseManager()
        self.assertFalse(disease_manager.is_cured(BLUE))
        self.assertFalse(disease_manager.is_eradicated(GREY))
        self.assertEqual(
            disease_manager.get_remaining_diseases(RED), DISEASE_CUBE_LIMIT)

    def test_cure_and_eradicate(self):
        disease_manager = DiseaseManager()
        self.assertFalse(disease_manager.is_cured(BLUE))
        disease_manager.cure_disease(BLUE)
        self.assertTrue(disease_manager.is_cured(BLUE))
        self.assertFalse(disease_manager.is_cured(RED))
        self.assertRaises(
            InvalidOperationError, lambda: disease_manager.eradicate_disease(RED))
        disease_manager.eradicate_disease(BLUE)
        self.assertTrue(disease_manager.is_eradicated(BLUE))

    def test_remove_and_place_disease(self):
        disease_manager = DiseaseManager()
        disease_manager.place_disease(RED)
        disease_manager.place_disease(BLUE, 4)
        self.assertEqual(disease_manager.get_remaining_diseases(
            RED), DISEASE_CUBE_LIMIT - 1)
        self.assertEqual(disease_manager.get_remaining_diseases(
            BLUE), DISEASE_CUBE_LIMIT - 4)
        disease_manager.remove_disease(BLUE, 3)
        disease_manager.remove_disease(RED)
        self.assertEqual(disease_manager.get_remaining_diseases(
            BLUE), DISEASE_CUBE_LIMIT - 1)
        self.assertEqual(disease_manager.get_remaining_diseases(
            RED), DISEASE_CUBE_LIMIT)
        self.assertRaises(GameEndedError, lambda: disease_manager.place_disease(
            GREY, DISEASE_CUBE_LIMIT + 1))


class TestCityCardMethods(unittest.TestCase):
    def test_init(self):
        test_deck = TestCityCardDeck()
        self.assertEqual(test_deck.sf.name, "San Francisco")
        self.assertEqual(test_deck.sf.color, BLUE)

    def test_eq(self):
        test_deck = TestCityCardDeck()
        sf = CityCard("San Francisco", BLUE)
        sf_city = City("San Francisco", BLUE)
        self.assertFalse(test_deck.sf == test_deck.mc)
        self.assertTrue(test_deck.sf == sf)
        self.assertTrue(test_deck.sf == sf_city)
        self.assertTrue(test_deck.mc != sf_city)
        self.assertTrue(test_deck.la != test_deck.mc)
        self.assertTrue(sf != test_deck.mc)


class TestInfectionCardMethods(unittest.TestCase):
    def test_infection_card_init(self):
        test_deck = TestInfectionCardDeck()
        sf = InfectionCard("San Francisco", BLUE)
        sf_city = TestMap().get_city("San Francisco")
        self.assertTrue(test_deck.sf == sf)
        self.assertTrue(test_deck.sf == sf_city)
        self.assertFalse(test_deck.sf == test_deck.mc)
        self.assertTrue(test_deck.sf != test_deck.la)
        self.assertTrue(sf != test_deck.la)

    def test_eq(self):
        test_deck = TestCityCardDeck()
        sf = InfectionCard("San Francisco", BLUE)
        sf_city_card_good = CityCard("San Francisco", BLUE)
        sf_city_card_bad = CityCard("San Francisco", YELLOW)
        sf_city = TestMap().get_city("San Francisco")
        self.assertFalse(test_deck.sf == test_deck.mc)
        self.assertTrue(test_deck.sf == sf)
        self.assertTrue(test_deck.sf == sf_city)
        self.assertTrue(test_deck.mc != sf_city)
        self.assertTrue(test_deck.la != test_deck.mc)
        self.assertTrue(sf != test_deck.mc)
        self.assertEqual(sf_city_card_good, test_deck.sf)
        self.assertEqual(sf_city_card_good, sf_city)
        self.assertEqual(sf_city_card_good, sf)
        self.assertNotEqual(sf_city_card_bad, test_deck.sf)


class TestCardManagerMethods(unittest.TestCase):
    def test_init(self):
        card_manager = CardManager()
        self.assertEqual(card_manager.infection_card_discard, [])
        self.assertEqual(card_manager.city_card_discard, [])

    def test_draw_and_discard_city_cards(self):
        card_manager = CardManager()
        length = len(card_manager.city_card_deck)
        cards = card_manager.draw_city_cards()
        self.assertTrue(len(cards), 2)
        self.assertEqual(len(card_manager.city_card_deck), length - 2)
        self.assertTrue(cards[0] not in card_manager.city_card_deck)
        self.assertTrue(cards[1] not in card_manager.city_card_deck)
        self.assertTrue(isinstance(cards[0], CityCard))
        card_manager.discard_city_cards(cards)
        self.assertEqual(cards, card_manager.city_card_discard)

    def test_draw_and_discard_infection_cards(self):
        card_manager = CardManager()
        length = len(card_manager.infection_card_deck)
        cards = card_manager.draw_infection_cards()
        self.assertEqual(len(cards), 2)
        self.assertEqual(len(card_manager.infection_card_deck), length - 2)
        self.assertTrue(cards[0] not in card_manager.infection_card_deck)
        self.assertTrue(cards[1] not in card_manager.infection_card_deck)
        self.assertEqual(cards, card_manager.infection_card_discard)
        bottom_card = card_manager.draw_bottom_infection_card()
        cards.extend([bottom_card])
        self.assertTrue(bottom_card not in card_manager.infection_card_deck)
        self.assertTrue(bottom_card in card_manager.infection_card_discard)
        card_manager.shuffle_and_replace_infection_cards()
        self.assertTrue(cards[0] in card_manager.infection_card_deck)
        self.assertTrue(cards[1] in card_manager.infection_card_deck)
        self.assertTrue(cards[2] in card_manager.infection_card_deck)
        self.assertEqual(card_manager.infection_card_discard, [])


class TestPlayerMethods(unittest.TestCase):
    def test_init(self):
        p = TestPlayer.get_test_player()
        self.assertEqual(p.current_city, TestMap().get_city("Atlanta"))
        self.assertEqual(p.player_id, "someidhere")
        self.assertEqual(p.city_cards, [])

    def test_move_adjacent(self):
        p = TestPlayer.get_test_player()
        self.assertTrue(p.move_adjacent(TestMap().get_city("Chicago")))
        self.assertTrue(p.move_adjacent(TestMap().get_city("Atlanta")))
        self.assertFalse(p.move_adjacent(TestMap().get_city("Atlanta")))
        self.assertFalse(p.move_adjacent(TestMap().get_city("Tokyo")))

    def test_move_direct_flight(self):
        p = TestPlayer.get_test_player()
        self.assertEqual(p.current_city, TestMap().get_city("Atlanta"))
        self.assertTrue(p.move_direct_flight(TestMap().get_city("Chicago")))
        self.assertFalse(p.move_direct_flight(TestMap().get_city("Chicago")))
        self.assertEqual(p.current_city, TestMap().get_city("Chicago"))

    def test_move_charter_flight(self):
        p = TestPlayer.get_test_player()
        self.assertTrue(p.move_charter_flight(
            TestMap().get_city("Atlanta"), TestMap().get_city("Tokyo")))
        self.assertFalse(p.move_charter_flight(
            TestMap().get_city("Atlanta"), TestMap().get_city("Chicago")))
        self.assertFalse(p.move_charter_flight(
            TestMap().get_city("Tokyo"), TestMap().get_city("Tokyo")))
        self.assertEqual(p.current_city, TestMap().get_city("Tokyo"))

    def test_move_shuttle_flight(self):
        p = TestPlayer.get_test_player()
        t = TestMap()
        cities = t.cities
        cities[t.get_city("Osaka").name].add_research_station()
        self.assertTrue(p.move_shuttle_flight(t.get_city("Osaka")))
        self.assertFalse(p.move_shuttle_flight(t.get_city("Osaka")))
        self.assertFalse(p.move_shuttle_flight(t.get_city("Tokyo")))


if __name__ == '__main__':
    unittest.main()
