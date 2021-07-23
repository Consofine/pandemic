import sys
sys.path.append('..')
import unittest
from board import *
from custom_exceptions import GameEndedError
from constants import *


class TestMap():
    def __init__(self):
        self.sf = City("San Francisco", BLUE)
        self.chi = City("Chicago", BLUE)
        self.la = City("Los Angeles", YELLOW)
        self.mc = City("Mexico City", YELLOW)
        self.sf.connected_cities = [self.chi, self.la]
        self.chi.connected_cities = [self.sf, self.mc]
        self.la.connected_cities = [self.sf, self.mc]
        self.mc.connected_cities = [self.chi, self.la]


class TestCityCardDeck():
    def __init__(self):
        self.sf = CityCard("San Francisco", BLUE)
        self.la = CityCard("Los Angeles", YELLOW)
        self.chi = CityCard("Chicago", BLUE)
        self.mc = CityCard("Mexico City", YELLOW)


class TestInfectionCardDeck():
    def __init__(self):
        self.sf = InfectionCard("San Francisco", BLUE)
        self.la = InfectionCard("Los Angeles", YELLOW)
        self.chi = InfectionCard("Chicago", BLUE)
        self.mc = InfectionCard("Mexico City", YELLOW)


class TestCityMethods(unittest.TestCase):
    def test_add_disease(self):
        test_map = TestMap()
        test_map.la.add_single_disease(BLUE)
        test_map.sf.add_single_disease(YELLOW)
        test_map.sf.add_single_disease(YELLOW)
        test_map.sf.add_single_disease(YELLOW)
        test_map.sf.add_single_disease(YELLOW)
        self.assertEqual(test_map.sf.disease_count[YELLOW], 3)
        self.assertEqual(test_map.chi.disease_count[YELLOW], 1)
        self.assertEqual(test_map.la.disease_count[YELLOW], 1)
        self.assertEqual(test_map.la.disease_count[BLUE], 1)
        self.assertEqual(test_map.mc.disease_count[YELLOW], 0)

    def test_trigger_outbreak(self):
        test_map = TestMap()
        test_map.sf.trigger_outbreak(YELLOW, [])
        test_map.la.trigger_outbreak(YELLOW, [test_map.mc])
        self.assertEqual(test_map.chi.disease_count[YELLOW], 1)
        self.assertEqual(test_map.la.disease_count[YELLOW], 1)
        self.assertEqual(test_map.mc.disease_count[BLUE], 0)

    def test_add_epidemic_disease(self):
        test_map = TestMap()
        test_map.chi.add_epidemic_disease(BLUE)
        self.assertEqual(test_map.chi.disease_count[BLUE], 3)
        test_map.chi.add_epidemic_disease(YELLOW)
        self.assertEqual(test_map.chi.disease_count[YELLOW], 3)
        self.assertEqual(test_map.chi.disease_count[RED], 0)
        self.assertEqual(test_map.chi.disease_count[GREY], 0)
        self.assertEqual(test_map.sf.disease_count[YELLOW], 0)
        test_map.chi.add_epidemic_disease(YELLOW)
        self.assertEqual(test_map.sf.disease_count[YELLOW], 1)
        self.assertEqual(test_map.mc.disease_count[YELLOW], 1)
        self.assertEqual(test_map.mc.disease_count[BLUE], 0)

    def test_treat_single_disease(self):
        test_map = TestMap()
        self.assertFalse(test_map.chi.treat_single_disease(BLUE))
        self.assertFalse(test_map.chi.add_epidemic_disease(BLUE))
        self.assertTrue(test_map.chi.treat_single_disease(BLUE))
        self.assertEqual(test_map.chi.disease_count[BLUE], 2)
        self.assertFalse(test_map.chi.treat_single_disease(YELLOW))

    def test_cure_all_disease(self):
        test_map = TestMap()
        self.assertFalse(test_map.chi.cure_all_disease(BLUE))
        self.assertFalse(test_map.la.add_epidemic_disease(GREY))
        self.assertTrue(test_map.la.cure_all_disease(GREY))
        self.assertFalse(test_map.la.cure_all_disease(GREY))
        self.assertEqual(test_map.la.disease_count[GREY], 0)

    def test_add_research_station(self):
        test_map = TestMap()
        self.assertTrue(test_map.sf.add_research_station())
        self.assertFalse(test_map.sf.add_research_station())


class TestInfectionStateMethods(unittest.TestCase):
    def test_infection_state_init(self):
        infect_state = InfectionState()
        self.assertEqual(infect_state.level, 1)
        self.assertEqual(infect_state.rate, 2)

    def test_infection_state_increase_level(self):
        infect_state = InfectionState()
        self.assertEqual(infect_state.level, 1)
        self.assertEqual(infect_state.rate, 2)
        infect_state.increase_level()
        self.assertEqual(infect_state.level, 2)
        self.assertEqual(infect_state.rate, 2)
        infect_state.increase_level()
        infect_state.increase_level()
        self.assertEqual(infect_state.rate, 3)
        self.assertEqual(infect_state.level, 4)


class TestDiseaseStateMethods(unittest.TestCase):
    def test_init(self):
        disease_state = DiseaseState()
        self.assertFalse(disease_state.is_cured(BLUE))
        self.assertFalse(disease_state.is_eradicated(GREY))
        self.assertEqual(
            disease_state.get_remaining_diseases(RED), DISEASE_CUBE_LIMIT)

    def test_cure_and_eradicate(self):
        disease_state = DiseaseState()
        self.assertFalse(disease_state.is_cured(BLUE))
        disease_state.cure_disease(BLUE)
        self.assertTrue(disease_state.is_cured(BLUE))
        self.assertFalse(disease_state.is_cured(RED))
        self.assertRaises(
            InvalidOperationError, lambda: disease_state.eradicate_disease(RED))
        disease_state.eradicate_disease(BLUE)
        self.assertTrue(disease_state.is_eradicated(BLUE))

    def test_remove_and_place_disease(self):
        disease_state = DiseaseState()
        disease_state.place_disease(RED)
        disease_state.place_disease(BLUE, 4)
        self.assertEqual(disease_state.get_remaining_diseases(
            RED), DISEASE_CUBE_LIMIT - 1)
        self.assertEqual(disease_state.get_remaining_diseases(
            BLUE), DISEASE_CUBE_LIMIT - 4)
        disease_state.remove_disease(BLUE, 3)
        disease_state.remove_disease(RED)
        self.assertEqual(disease_state.get_remaining_diseases(
            BLUE), DISEASE_CUBE_LIMIT - 1)
        self.assertEqual(disease_state.get_remaining_diseases(
            RED), DISEASE_CUBE_LIMIT)
        self.assertRaises(GameEndedError, lambda: disease_state.place_disease(
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
        sf_city = City("San Francisco", BLUE)
        self.assertTrue(test_deck.sf == sf)
        self.assertTrue(test_deck.sf == sf_city)
        self.assertFalse(test_deck.sf == test_deck.mc)
        self.assertTrue(test_deck.sf != test_deck.la)
        self.assertTrue(sf != test_deck.la)


class TestCardStateMethods(unittest.TestCase):
    def test_init(self):
        card_state = CardState()
        self.assertEqual(card_state.infection_card_discard, [])
        self.assertEqual(card_state.city_card_discard, [])

    def test_draw_and_discard_city_cards(self):
        card_state = CardState()
        length = len(card_state.city_card_deck)
        cards = card_state.draw_city_cards()
        self.assertTrue(len(cards), 2)
        self.assertEqual(len(card_state.city_card_deck), length - 2)
        self.assertTrue(cards[0] not in card_state.city_card_deck)
        self.assertTrue(cards[1] not in card_state.city_card_deck)
        self.assertTrue(isinstance(cards[0], CityCard))
        card_state.discard_city_cards(cards)
        self.assertEqual(cards, card_state.city_card_discard)

    def test_draw_and_discard_infection_cards(self):
        card_state = CardState()
        length = len(card_state.infection_card_deck)
        cards = card_state.draw_infection_cards()
        self.assertEqual(len(cards), 2)
        self.assertEqual(len(card_state.infection_card_deck), length - 2)
        self.assertTrue(cards[0] not in card_state.infection_card_deck)
        self.assertTrue(cards[1] not in card_state.infection_card_deck)
        self.assertEqual(cards, card_state.infection_card_discard)
        bottom_card = card_state.draw_bottom_infection_card()
        cards.extend([bottom_card])
        self.assertTrue(bottom_card not in card_state.infection_card_deck)
        self.assertTrue(bottom_card in card_state.infection_card_discard)
        card_state.shuffle_and_replace_infection_cards()
        self.assertTrue(cards[0] in card_state.infection_card_deck)
        self.assertTrue(cards[1] in card_state.infection_card_deck)
        self.assertTrue(cards[2] in card_state.infection_card_deck)
        self.assertEqual(card_state.infection_card_discard, [])
