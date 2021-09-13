import sys
sys.path.append('..')
import unittest
import functools
from board import *
from custom_exceptions import GameEndedError
from constants import *


class TestMap():
    def __init__(self):
        self.cities = Board.init_cities(STARTING_CITY)

    def get_city(self, city_name: str) -> City:
        return self.cities[city_name]

    def get_city_card(self, city_name: str) -> CityCard:
        return CityCard(city_name)


class TestPlayer:
    @classmethod
    def get_test_player(self) -> Player:
        cities: dict = Board.init_cities(STARTING_CITY)
        p = Player("someidhere", Role(), cities[STARTING_CITY])
        p.add_card(CityCard("San Francisco"))
        p.add_card(CityCard("Algiers"))
        p.add_card(CityCard("Karachi"))
        return p

    @classmethod
    def get_second_test_player(self) -> Player:
        cities: dict = Board.init_cities(STARTING_CITY)
        p = Player("anotheridhere", Role(), cities[STARTING_CITY])
        p.add_card(CityCard("Atlanta"))
        p.add_card(CityCard("Osaka"))
        p.add_card(CityCard("Tokyo"))
        p.add_card(CityCard("Jakarta"))
        p.add_card(CityCard("Chennai"))
        return p

    @classmethod
    def get_can_cure_red_player(self) -> Player:
        cities: dict = Board.init_cities(STARTING_CITY)
        p = Player("thisonecancure", Role(), cities[STARTING_CITY])
        p.add_card(CityCard("Tokyo"))
        p.add_card(CityCard("Shanghai"))
        p.add_card(CityCard("Beijing"))
        p.add_card(CityCard("Sydney"))
        p.add_card(CityCard("Jakarta"))
        return p


class TestCityCardDeck:
    def __init__(self):
        self.sf = CityCard("San Francisco")
        self.la = CityCard("Los Angeles")
        self.chi = CityCard("Chicago")
        self.mc = CityCard("Mexico City")


class TestInfectionCardDeck:
    def __init__(self):
        self.sf = InfectionCard("San Francisco")
        self.la = InfectionCard("Los Angeles")
        self.chi = InfectionCard("Chicago")
        self.mc = InfectionCard("Mexico City")


class TestCityMethods(unittest.TestCase):
    def test_city_init(self):
        t = TestMap()
        test_sf = t.get_city("San Francisco")
        self.assertEqual(test_sf.name, "San Francisco")
        self.assertEqual(test_sf.color, BLUE)
        self.assertFalse(test_sf.has_research_station)
        mc = t.get_city("Mexico City")
        mc = City(mc)
        self.assertTrue(isinstance(mc, City))

    def test_eq(self):
        test_sf = TestMap().get_city("San Francisco")
        self.assertEqual(test_sf, CityCard(
            "San Francisco"))
        self.assertNotEqual(test_sf, CityCard("Tokyo"))

    def test_add_disease(self):
        test_map = TestMap()
        self.assertFalse(test_map.get_city(
            "Los Angeles").add_single_disease(test_map.cities, BLUE))
        self.assertFalse(test_map.get_city(
            "San Francisco").add_single_disease(test_map.cities, YELLOW))
        self.assertFalse(test_map.get_city(
            "San Francisco").add_single_disease(test_map.cities, YELLOW))
        self.assertFalse(test_map.get_city(
            "San Francisco").add_single_disease(test_map.cities, YELLOW))
        self.assertTrue(test_map.get_city(
            "San Francisco").add_single_disease(test_map.cities, YELLOW))
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
        test_map.get_city("San Francisco").trigger_outbreak(
            test_map.cities, YELLOW, [])
        test_map.get_city("Los Angeles").trigger_outbreak(test_map.cities,
                                                          YELLOW, [test_map.get_city("Mexico City")])
        self.assertEqual(test_map.get_city("Chicago").disease_count[YELLOW], 2)
        self.assertEqual(test_map.get_city(
            "Los Angeles").disease_count[YELLOW], 1)
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[BLUE], 0)
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[YELLOW], 0)

        test_map.get_city("Chicago").trigger_outbreak(
            test_map.cities, BLUE, [])
        self.assertEqual(test_map.get_city(
            "Mexico City").disease_count[BLUE], 1)
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[BLUE], 1)
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[YELLOW], 1)

    def test_add_epidemic_disease(self):
        test_map = TestMap()
        self.assertFalse(test_map.get_city(
            "Chicago").add_epidemic_disease(test_map.cities, BLUE))
        self.assertEqual(test_map.get_city("Chicago").disease_count[BLUE], 3)
        self.assertFalse(test_map.get_city(
            "Chicago").add_epidemic_disease(test_map.cities, YELLOW))
        self.assertEqual(test_map.get_city("Chicago").disease_count[YELLOW], 3)
        self.assertEqual(test_map.get_city("Chicago").disease_count[RED], 0)
        self.assertEqual(test_map.get_city("Chicago").disease_count[GREY], 0)
        self.assertEqual(test_map.get_city(
            "San Francisco").disease_count[YELLOW], 0)
        self.assertTrue(test_map.get_city(
            "Chicago").add_epidemic_disease(test_map.cities, YELLOW))
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
            "Chicago").add_epidemic_disease(test_map.cities, BLUE))
        self.assertTrue(test_map.get_city(
            "Chicago").treat_single_disease(BLUE))
        self.assertEqual(test_map.get_city("Chicago").disease_count[BLUE], 2)
        self.assertFalse(test_map.get_city(
            "Chicago").treat_single_disease(YELLOW))

    def test_treat_all_disease(self):
        test_map = TestMap()
        test_map.get_city("San Francisco").add_epidemic_disease(
            test_map.cities, BLUE)
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

    def test_infection_manager_increase_outbreak_count(self):
        im = InfectionManager()
        for _ in range(MAX_OUTBREAK_COUNT - 1):
            im.increase_outbreak_count()
        self.assertRaises(GameEndedError, im.increase_outbreak_count)


class TestDiseaseManagerMethods(unittest.TestCase):
    def test_init(self):
        disease_manager = DiseaseManager()
        self.assertFalse(disease_manager.is_cured(BLUE))
        self.assertFalse(disease_manager.is_eradicated(GREY))
        self.assertEqual(
            disease_manager.get_remaining_diseases(RED), DISEASE_CUBE_LIMIT)

    def test_get_remaining_diseases(self):
        dm = DiseaseManager()
        ret = dm.get_remaining_diseases()
        self.assertEqual(len(set(ret.values())), 1)
        self.assertTrue(DISEASE_CUBE_LIMIT in set(ret.values()))
        self.assertEqual(dm.get_remaining_diseases(BLUE), DISEASE_CUBE_LIMIT)
        dm.place_disease(BLUE)
        ret = dm.get_remaining_diseases()
        self.assertEqual(ret[BLUE], DISEASE_CUBE_LIMIT - 1)
        self.assertEqual(len(set(ret.values())), 2)

    def test_is_cured_or_eradicated(self):
        dm = DiseaseManager()
        dm.cure_disease(RED)
        self.assertTrue(dm.is_cured(RED))
        self.assertFalse(dm.is_cured(BLUE))
        dm.eradicate_disease(RED)
        self.assertTrue(dm.is_eradicated(RED))
        self.assertRaises(InvalidOperationError, dm.eradicate_disease, BLUE)

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
        sf = CityCard("San Francisco")
        sf_city = City("San Francisco")
        self.assertFalse(test_deck.sf == test_deck.mc)
        self.assertTrue(test_deck.sf == sf)
        self.assertTrue(test_deck.sf == sf_city)
        self.assertTrue(test_deck.mc != sf_city)
        self.assertTrue(test_deck.la != test_deck.mc)
        self.assertTrue(sf != test_deck.mc)


class TestInfectionCardMethods(unittest.TestCase):
    def test_infection_card_init(self):
        test_deck = TestInfectionCardDeck()
        sf = InfectionCard("San Francisco")
        sf_city = TestMap().get_city("San Francisco")
        self.assertTrue(test_deck.sf == sf)
        self.assertTrue(test_deck.sf == sf_city)
        self.assertFalse(test_deck.sf == test_deck.mc)
        self.assertTrue(test_deck.sf != test_deck.la)
        self.assertTrue(sf != test_deck.la)

    def test_eq(self):
        test_deck = TestCityCardDeck()
        sf = InfectionCard("San Francisco")
        sf_city_card_good = CityCard("San Francisco")
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


class TestCardManagerMethods(unittest.TestCase):
    def test_init(self):
        card_manager = CardManager()
        self.assertEqual(card_manager.infection_card_discard, [])
        self.assertEqual(card_manager.city_card_discard, [])

    def test_init_city_cards(self):
        card_manager = CardManager()
        card_manager.init_city_cards()
        self.assertTrue(len(card_manager.city_card_deck)
                        == len(CITY_LIST.keys()) + MIN_NUM_EPIDEMIC_CARDS)
        self.assertTrue(
            len(set([c.color for c in card_manager.city_card_deck if not isinstance(c, EpidemicCard)])) == 4)

    def test_init_infection_cards(self):
        card_manager = CardManager()
        card_manager.init_infection_cards()
        self.assertTrue(len(card_manager.infection_card_deck)
                        == len(CITY_LIST.keys()))
        self.assertTrue(
            len(set([c.color for c in card_manager.infection_card_deck])) == 4)

    def test_draw_and_discard_city_cards_no_epidemics(self):
        card_manager = CardManager(0)
        length = len(card_manager.city_card_deck)
        cards = card_manager.draw_city_cards()
        self.assertTrue(len(cards), 2)
        self.assertEqual(len(card_manager.city_card_deck), length - 2)
        self.assertTrue(cards[0] not in card_manager.city_card_deck)
        self.assertTrue(cards[1] not in card_manager.city_card_deck)
        self.assertTrue(isinstance(cards[0], CityCard))
        card_manager.discard_city_cards(cards)
        self.assertEqual(cards, card_manager.city_card_discard)

    def test_draw_and_discard_city_cards(self):
        card_manager = CardManager()
        cards = card_manager.draw_city_cards()
        card_length = len(cards)
        while not isinstance(cards[0], EpidemicCard) and not isinstance(cards[1], EpidemicCard):
            cards = card_manager.draw_city_cards()
            card_length += len(cards)
        card_length += len(cards)
        self.assertEqual(len(card_manager.infection_card_discard), 0)
        self.assertEqual(len(card_manager.infection_card_deck),
                         len(CITY_LIST.keys()))

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

    def test_shuffle_and_replace_infection_cards(self):
        card_manager = CardManager()
        infection_discards = card_manager.draw_infection_cards()
        infection_discards.extend(card_manager.draw_infection_cards())
        self.assertTrue(len(infection_discards) == 4)
        self.assertTrue(functools.reduce(lambda a, b: a and b, [
                        c not in card_manager.infection_card_deck for c in infection_discards]))
        card_manager.shuffle_and_replace_infection_cards()
        self.assertTrue(functools.reduce(lambda a, b: a and b, [
                        c in card_manager.infection_card_deck[:len(infection_discards)] for c in infection_discards]))
        while len(card_manager.infection_card_deck) > 0:
            card_manager.draw_infection_cards()
        infection_discards = card_manager.draw_infection_cards()
        self.assertEqual(len(infection_discards), 2)

    def test_draw_bottom_infection_card(self):
        card_manager = CardManager()
        bottom_card = card_manager.draw_bottom_infection_card()
        self.assertEqual(len(card_manager.infection_card_deck),
                         len(CITY_LIST) - 1)
        self.assertTrue(bottom_card not in card_manager.infection_card_deck)
        self.assertEqual(card_manager.infection_card_discard, [bottom_card])


class TestPlayerMethods(unittest.TestCase):
    def test_init(self):
        p = TestPlayer.get_test_player()
        self.assertEqual(p.current_city, TestMap().get_city("Atlanta"))
        self.assertEqual(p.player_id, "someidhere")
        self.assertEqual(p.city_cards, [CityCard("San Francisco"),
                                        CityCard("Algiers"), CityCard("Karachi")])

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
        p = TestPlayer.get_second_test_player()
        t = TestMap()
        self.assertTrue(p.move_charter_flight(
            t.get_city_card("Atlanta"), t.get_city("Tokyo")))
        self.assertFalse(p.move_charter_flight(
            t.get_city_card("Atlanta"), t.get_city("Chicago")))
        self.assertFalse(p.move_charter_flight(
            t.get_city_card("Tokyo"), t.get_city("Tokyo")))
        self.assertEqual(p.current_city, t.get_city("Tokyo"))

    def test_move_shuttle_flight(self):
        p = TestPlayer.get_test_player()
        t = TestMap()
        cities = t.cities
        cities[t.get_city("Osaka").name].add_research_station()
        self.assertTrue(p.move_shuttle_flight(t.get_city("Osaka")))
        self.assertFalse(p.move_shuttle_flight(t.get_city("Osaka")))
        self.assertFalse(p.move_shuttle_flight(t.get_city("Tokyo")))
        self.assertTrue(p.move_shuttle_flight(t.get_city("Atlanta")))

    def test_give_knowledge(self):
        p1 = TestPlayer.get_test_player()
        p2 = TestPlayer.get_second_test_player()
        self.assertFalse(p1.give_knowledge(
            CityCard("Algiers"), p2))
        self.assertFalse(
            CityCard("Algiers") in p2.city_cards)
        self.assertFalse(
            CityCard("Algiers") not in p1.city_cards)
        self.assertFalse(p1.give_knowledge(
            CityCard("Karachi"), p2))
        self.assertFalse(p1.give_knowledge(
            CityCard("San Francisco"), p2))
        self.assertFalse(p2.give_knowledge(
            CityCard("Algiers"), p1))
        self.assertFalse(p2.give_knowledge(
            CityCard("Chennai"), p1))
        self.assertTrue(p2.give_knowledge(CityCard("Atlanta"), p1))
        self.assertTrue(CityCard("Atlanta") not in p2.city_cards)
        self.assertTrue(CityCard("Atlanta") in p1.city_cards)
        self.assertTrue(p1.give_knowledge(CityCard("Atlanta"), p2))
        self.assertTrue(CityCard("Atlanta") not in p1.city_cards)
        self.assertTrue(CityCard("Atlanta") in p2.city_cards)

    def test_add_card(self):
        p = TestPlayer.get_test_player()
        self.assertTrue(p.add_card(
            CityCard("Beijing")))
        self.assertTrue(p.add_card(
            CityCard("Shanghai")))
        self.assertFalse(p.add_card(
            CityCard("Shanghai")))
        self.assertTrue(p.add_card(
            CityCard("Tehran")))
        self.assertTrue(p.add_card(
            CityCard("Miami")))
        self.assertFalse(p.add_card(
            CityCard("Chicago")))

    def test_subtract_card(self):
        p = TestPlayer.get_test_player()
        self.assertTrue(p.subtract_card(
            CityCard("San Francisco")))
        self.assertFalse(p.subtract_card(
            CityCard("San Francisco")))
        self.assertTrue(p.subtract_card(
            CityCard("Algiers")))
        self.assertTrue(p.subtract_card(
            CityCard("Karachi")))

    def test_can_discover_cure(self):
        p1 = TestPlayer.get_can_cure_red_player()
        p2 = TestPlayer.get_second_test_player()
        self.assertTrue(p1.can_discover_cure(RED))
        self.assertTrue(p1.can_discover_cure(RED, p1.city_cards))
        self.assertFalse(p1.can_discover_cure(BLUE))
        self.assertFalse(p2.can_discover_cure(BLUE))
        p2.subtract_card(CityCard("Atlanta"))
        p2.add_card(CityCard("Beijing"))
        p2.add_card(CityCard("Seoul"))
        self.assertTrue(p2.can_discover_cure(RED))
        self.assertFalse(p2.can_discover_cure(BLUE))

    def test_discover_cure(self):
        p1 = TestPlayer.get_can_cure_red_player()
        p2 = TestPlayer.get_second_test_player()
        self.assertRaises(InvalidOperationError, p1.discover_cure, RED, [])
        p1.discover_cure(RED, p1.city_cards)
        self.assertRaises(InvalidOperationError,
                          p1.discover_cure, RED, p1.city_cards)
        self.assertRaises(InvalidOperationError,
                          p2.discover_cure, RED, p2.city_cards)

    def test_has_actions_left(self):
        p1 = TestPlayer.get_test_player()
        p2 = TestPlayer.get_second_test_player()
        p1.make_active()
        self.assertTrue(p1.has_actions_left())
        for _ in range(MAX_ACTIONS):
            p1.dec_actions_left()
        self.assertFalse(p1.has_actions_left())
        self.assertFalse(p2.has_actions_left())

    def test_dec_actions(self):
        p1 = TestPlayer.get_test_player()
        p1.make_active()
        while p1.has_actions_left():
            p1.dec_actions_left()
        self.assertFalse(p1.has_actions_left())


if __name__ == '__main__':
    unittest.main()
