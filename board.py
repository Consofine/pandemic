from typing import List, Union
import ipdb
import random
import jsonpickle
from enum import Enum
from custom_exceptions import GameEndedError, InvalidGametypeError, InvalidOperationError
from constants import *


class Serializer:
    @classmethod
    def get_game_object(id):
        """
        Class method for deserializing the game object from a json file
        Returns:
            game_object - GameManager object holding all information needed to play game
        """
        with open("game-{}.json".format(id), "r") as f:
            game_object = jsonpickle.decode(f.read())
        return game_object

    @classmethod
    def save_game_object(game_object, id):
        """
        Class method for serializing game object to a json file
        Args:
            game_object - GameManager object holding all information needed to play game
        """
        with open("game-{}.json".format(id), "w+") as f:
            f.write(jsonpickle.encode(game_object))


class Validator:
    """
    Object containing methods for validating different types of objects
    """
    @classmethod
    def validate_color(color):
        """
        Ensure that provided object is actually a Color
        """
        if color not in COLORS:
            raise InvalidGametypeError(Color, color)

    @classmethod
    def validate_city(city):
        """
        Ensure that provided object is actually a City
        """
        if not isinstance(city, City):
            raise InvalidGametypeError(City, city)

    @classmethod
    def validate_city_card(city_card):
        """
        Ensure that provided object is actually a CityCard
        """
        if not isinstance(city_card, CityCard):
            raise InvalidGametypeError(CityCard, city_card)


class Role:
    """
    Used to represent specific power of each player
    """

    def __init__(self):
        self.power


class Color:
    """
    Used to represent colors as an object
    """

    def __init__(self, color):
        if color not in COLORS:
            raise ValueError("Tried to create a Color without a valid color")
        self.color = color

    def __eq__(self, other) -> bool:
        if isinstance(other, Color):
            return self.color == other.color
        if isinstance(other, str):
            return self.color == other
        return False


class City():
    """
    Representing a board location and its state
    """

    def __init__(self, name: str, color):
        self.name: str = name
        self.color = color
        self.disease_count: dict = dict.fromkeys(
            [RED, BLUE, YELLOW, GREY], 0)
        self.has_research_station: bool = False
        self.connected_cities: Union[List, List[City]] = []

    def __eq__(self, other):
        """
        (in)Equality based on whether cities share name
        """
        if not isinstance(other, City) and not isinstance(other, CityCard):
            return False
        return self.name == other.name

    def set_connected_cities(self, cities: List[str]):
        """
        Stores list of cities cities as being adjacent to this
        Args:
            cities - list of cities that should be connected to this one
        """
        self.connected_cities = cities

    def add_single_disease(self, color, prior_outbreaks: Union[List, List['City']] = []) -> bool:
        """
        Adds one disease cube to this city. If this city already has MAX_DISEASE_COUNT
        disease cubes of given color, doesn't increase this city's count but triggers
        outbreak in neighboring cities
        Args:
            color - color of disease to increase here
            prior_outbreaks - (OPT) array used to track that this city has been hit
        Returns:
            bool - true if outbreak triggered, false otherwise
        """
        if self.disease_count[color] < MAX_DISEASE_COUNT:
            self.disease_count[color] += 1
            return False
        prior_outbreaks.append(self)
        self.trigger_outbreak(color, prior_outbreaks)
        return True

    def add_epidemic_disease(self, color) -> bool:
        """
        Adds three disease cubes to this city as part of an outbreak. If this city already has any
        disease cubes of the given color, then this city's disease_count for that color is capped at
        MAX_DISEASE_COUNT and an outbreak is triggered.
        Args:
            color - color of disease to add here
        Returns:
            bool - true if outbreak triggered, false otherwise
        """
        if self.disease_count[color] == 0:
            self.disease_count[color] = MAX_DISEASE_COUNT
            return False
        self.disease_count[color] = MAX_DISEASE_COUNT
        self.trigger_outbreak(color, [])
        return True

    def trigger_outbreak(self, color, prior_outbreaks: Union[List, List['City']]) -> None:
        """
        Adds one disease cube of given color to each connected city. Prevents infinite loops / chaining
        back to cities that have already been hit, but allows for chaining otherwise
        Args:
            color - color of disease that is outbreaking
            prior_outbreaks - array to track cities that have been hit by this outbreak chain
        """
        for city in self.connected_cities:
            if city not in prior_outbreaks:
                city.add_single_disease(color, prior_outbreaks)

    def treat_single_disease(self, color) -> bool:
        """
        Remove a single disease cube of a given color from this city
        Args:
            color - color of disease to remove
        Returns:
            bool - true if disease successfully removed, false if no disease of given color exists here
        """
        if self.disease_count[color] == 0:
            return False
        self.disease_count[color] -= 1
        return True

    def cure_all_disease(self, color) -> bool:
        """ and if CityCard matches.
        Remove all disease cubes of a given color from this city.
        Args:
            color - color of disease to remove
        Returns:
            bool - true if disease successfully removed, false if no disease of given color exists here
        """
        if self.disease_count[color] == 0:
            return False
        self.disease_count[color] = 0
        return True

    def add_research_station(self) -> bool:
        """
        Adds research station if none exists here already.
        Returns: 
            bool - True if research station successfully placed, False otherwise
        """
        if not self.has_research_station:
            self.has_research_station = True
            return True
        return False


class Player:
    """
    Represents one player (including location, powers, and state) from the game
    """

    def __init__(self, player_id, role, starting_city):
        self.player_id = player_id
        self.role = role
        self.is_active = False
        self.city_cards = []
        self.current_city = starting_city

    def move_adjacent(self, city):
        """
        Move player to an adjacent City and decrements number of actions left.
        Args:
            city - City to move to
        Returns:
            bool - true if move is successful, false otherwise
        """
        if self.actions_left > 0 and city in self.current_city.connected_cities:
            self.current_city = city
            self.actions_left -= 1
            return True
        return False

    def move_direct_flight(self, city: City):
        """
        Move player to the city on the card being played.
        Args:
            city - CityCard representing city to move to
        Returns:
            bool - True if move is successful, False otherwise
        """
        if city != self.current_city:
            self.current_city = city
            return True
        return False

    def move_charter_flight(self, curr_city, dest_city):
        """
        When player plays city card matching their current location, move them
        to any city they choose.
        Args:
            curr_city: CityCard of player's current location
            dest_city: City to which player is moving
        Returns:
            bool - true if move is successful, false otherwise
        """
        if self.actions_left > 0 and dest_city != self.current_city and curr_city == self.current_city:
            self.current_city = dest_city
            self.actions_left -= 1
            return True
        return False

    def move_shuttle_flight(self, dest_city):
        """
        Allows player to move from any city with a research station to any
        other city with a research station
        Args:
            dest_city - City to which player is moving
        Returns:
            bool - true if move is successful, false otherwise
        """
        if not Validator.validate_city(dest_city):
            raise InvalidGametypeError(City, dest_city)
        if self.actions_left > 0 and self.current_city.has_research_station and dest_city.has_research_station:
            self.current_city = dest_city
            self.actions_left -= 1
            return True
        return False


class Card:
    """
    Parent class holding city name and color
    """

    def __init__(self, city_name: str, color):
        if not city_name in CITY_LIST or color not in COLORS:
            raise ValueError("Invalid argument passed to Card constructor")
        self.name: str = city_name
        self.color = color

    def __eq__(self, other: object) -> bool:
        """
        (in)Equality based on whether cities share name
        """
        if not isinstance(other, City) and not isinstance(other, CityCard):
            return False
        return self.name == other.name


class CityCard(Card):
    """
    Representing the type of card used to cure diseases and travel.
    """

    def __init__(self, city_name: str, color):
        super().__init__(city_name, color)


class InfectionCard(Card):
    """
    Representing the type of card that is drawn at the end of each turn and used to
    place new infections in certain cities.
    """

    def __init__(self, city_name: str, color):
        super().__init__(city_name, color)


class CardManager:
    """
    Object for storing CityCard deck and InfectionCard deck, along with methods for accessing
    """

    def __init__(self):
        self.city_card_deck = self.init_city_cards()
        self.city_card_discard = []
        self.infection_card_deck = self.init_infection_cards()
        self.infection_card_discard = []

    def init_city_cards(self) -> List[CityCard]:
        """
        Creates a deck of CityCards using the city_list constant
        Returns:
            [CityCard] - deck of CityCards for game
        """
        return [CityCard(c, CITY_LIST[c]) for c in CITY_LIST.keys()]

    def init_infection_cards(self) -> List[InfectionCard]:
        """
        Creates a deck of InfectionCards using the city_list constant
        Returns:
            [InfectionCard] - deck of InfectionCards for game
        """
        return [InfectionCard(c, CITY_LIST[c]) for c in CITY_LIST.keys()]

    def draw_city_cards(self) -> List[CityCard]:
        """
        Removes 2 CityCards from the top of the deck. If there aren't 2 CityCards remaining, throws error
        Returns:
            CityCards - array of 2 city cards
        Throws:
            GameEndedError
                -if not 2 CityCards remaining
        """
        if len(self.city_card_deck) < 2:
            raise GameEndedError("Not enough City Cards remaining")
        city_cards = self.city_card_deck[0:2]
        del self.city_card_deck[0:2]
        return city_cards

    def discard_city_cards(self, city_cards: List[CityCard]) -> None:
        """
        Takes array of city cards and puts them in the discard pile. Cards are prepended to
        city card discard deck, although this shouldn't really ever be relevant
        Args:
            city_cards: array of city cards to discard
        """
        self.city_card_discard[:0] = city_cards

    def draw_infection_cards(self, number: int = 2) -> List[InfectionCard]:
        """
        Removes InfectionCards from top of InfectionCard deck. Adds these to discard pile,
        since they won't be added to anyone's hand.
        Returns:
            InfectionCards - array of drawn infection cards
        """
        if len(self.infection_card_deck) < number:
            raise InvalidOperationError("Not enough Infection Cards remaining")
        infection_cards = self.infection_card_deck[0:number]
        self.infection_card_discard[:0] = infection_cards
        del self.infection_card_deck[0:number]
        return infection_cards

    def shuffle_and_replace_infection_cards(self) -> None:
        """
        Method used after an epidemic card is drawn. Shuffles the infection card discard pile and
        puts those cards on top of the infection card deck
        """
        random.shuffle(self.infection_card_discard)
        self.infection_card_discard.extend(self.infection_card_deck)
        self.infection_card_deck = self.infection_card_discard
        self.infection_card_discard = []

    def draw_bottom_infection_card(self) -> InfectionCard:
        """
        Method used after an epidemic card is drawn. Returns bottom infection card from infection card
        deck, but also adds this card to the top of the infection card discard pile
        Returns:
            InfectionCard - bottom card from deck
        """
        bottom_card = self.infection_card_deck.pop()
        self.infection_card_discard[:0] = [bottom_card]
        return bottom_card

    def handle_action(self, action, *positional_args, **keyword_args):
        action(positional_args, keyword_args)


class PlayerManager:
    def __init__(self, player_ids: List[str], starting_city: City = City(STARTING_CITY, CITY_LIST[STARTING_CITY])):
        self.active_player: Union[Player, None] = None
        self.players: List[Player] = [Player(p, "TODO-role", starting_city)
                                      for p in player_ids]
        self.set_active_player(self.players[0])

    def set_active_player(self, player: Player) -> None:
        """
        Set the active player to be the given player object. Also, set all other
        players' active statuses to False, and set this player's active status to True.
        Args:
            Player - a Player object representing the new active player
        """
        for p in self.players:
            if p == player:
                self.active_player = p
                p.is_active = True
            else:
                p.is_active = False


class InfectionManager:
    """
    Object for tracking current infection level and rate. Separate from disease state, which holds
    number of remaining diseases left for each color
    """

    def __init__(self):
        self.level = 1
        self.rate = 2
        self.outbreak_count = 0
        self.rates = {
            1: 2,
            2: 2,
            3: 2,
            4: 3,
            5: 3,
            6: 4,
            7: 4
        }

    def increase_level(self) -> None:
        """
        Increase infection level by one, which may increase the current rate
        """
        self.level += 1
        self.rate = self.rates[self.level]

    def increase_outbreak_count(self) -> bool:
        """
        Increase the outbreak level. If we hit the max number of outbreaks, return true else false
        """
        self.outbreak_count += 1
        return self.outbreak_count < MAX_OUTBREAK_COUNT


class DiseaseManager:
    """
    Object for holding data about remaining diseases and disease statuses(cured / eradicated)
    """

    def __init__(self):
        self.diseases_cured = dict.fromkeys(COLORS, False)
        self.diseases_eradicated = dict.fromkeys(COLORS, False)
        self.diseases_remaining = dict.fromkeys(COLORS, DISEASE_CUBE_LIMIT)

    def get_remaining_diseases(self, color=None) -> dict:
        """
        Returns the dict of remaining diseases, or the count remaining for a specific disease color
        if provided
        Args:
            color(opt) - string representing color of disease
        """
        if color is not None:
            return self.diseases_remaining[color]
        return self.diseases_remaining

    def is_cured(self, color) -> bool:
        """
        Check if a disease has been cured already
        Args:
            color - string representing color of disease being checked
        Returns:
            bool - True if disease is cured, else false
        """
        return self.diseases_cured[color]

    def is_eradicated(self, color) -> bool:
        """
        Check if a disease has been eradicated already
        Args:
            color - string representing color of disease being checked
        Returns:
            bool - True if disease is eradicated, else false
        """
        return self.diseases_eradicated[color]

    def cure_disease(self, color) -> None:
        """
        Set a disease's status to cured.
        Args:
            color - string representing color of disease being cured
        """
        self.diseases_cured[color] = True

    def eradicate_disease(self, color) -> None:
        """
        Set a disease's status to eradicated, given that the disease has been cured
        Args:
            color - string representing color of disease being eradicated
        Raises:
            InvalidOperationsError
                -if disease color hasn't been cured yet
        """
        if not self.is_cured(color):
            raise InvalidOperationError(
                "Can't eliminate disease before curing")
        self.diseases_eradicated[color] = True

    def place_disease(self, color, number: int = 1) -> None:
        """
        Call this when a disease cube has been placed on the board(therefore decreasing the number of that disease remaining)
        Args:
            color - string representing color of disease being placed
            number(opt) - number of disease cubes to place
        Raises:
            GameEndedError
                -if we've run out of diseases
        """
        if self.diseases_remaining[color] < number:
            raise GameEndedError(
                "You ran out of disease cubes for the color {}".format(color))
        self.diseases_remaining[color] -= number

    def remove_disease(self, color, number: int = 1) -> None:
        """
        Call this when a disease cube has been treated
        Args:
            color - string representing color of disease being placed
            number(opt) - number of disease cubes to place
        """
        self.diseases_remaining[color] += number


class GameManager:
    """
    Object holding state information relevant to the game as a whole
    """

    def __init__(self, game_id: str, player_ids: List[str]) -> None:
        self.game_id: str = game_id
        self.infection_manager: InfectionManager = InfectionManager()
        self.disease_manager: DiseaseManager = DiseaseManager()
        self.card_manager: CardManager = CardManager()
        self.player_manager: PlayerManager = PlayerManager(player_ids)
        self.cities: dict = self.init_cities()

    def init_cities(self) -> dict:
        """
        Using cities and connected cities information from constants file,
        creates a dict holding all cities with all of their related data
        Returns: 
            cities - dict associating city names to city objects for all 48 cities
        """
        cities = {c: City(c, CITY_LIST[c]) for c in CITY_LIST.keys()}
        for city in cities.values():
            city.set_connected_cities(CITY_CONNECTIONS[city.name])
        cities[STARTING_CITY].add_research_station()
        return cities


class ActionList(Enum):
    """
    Enum holding the 8 standard actions that a player can take on their turn.
    TODO: make this include player-specific actions
    """
    move_adjacent = MOVE_ADJACENT
    move_direct_flight = MOVE_DIRECT_FLIGHT
    move_charter_flight = MOVE_CHARTER_FLIGHT
    move_shuttle_flight = MOVE_SHUTTLE_FLIGHT
    build_research_station = BUILD_RESEARCH_STATION
    treat_disease = TREAT_DISEASE
    share_knowledge = SHARE_KNOWLEDGE
    discover_cure = DISCOVER_CURE


class ActionManager():
    def __init__(self):
        self.action_list = ActionList()
        pass

    def make_move(self, action: int, *args, **kwargs):
        pass

    def move_adjacent(self, player: Player, end_city: City):
        return player.move_adjacent(end_city)

    def move_direct_flight(self, player):
        pass

    def move_charter_flight(self):
        pass

    def move_shuttle_flight(self):
        pass

    def build_research_station(self):
        pass

    def treat_disease(self):
        pass

    def share_knowledge(self):
        pass

    def cure_disease(self):
        pass


class Board:
    """
    Holds game state, list of cities, and players (with their positions)
    etc
    """

    def __init__(self, game_id, player_ids):
        # set up game state
        self.game_state = GameManager(game_id, player_ids)
        self.actions = Action()

    def make_action(self):
        # TODO
        return

    def use_ability(self):
        # TODO
        return

    def end_of_actions(self):
        # draw city cards and give them to the active player
        self.game_state.player_manager.active_player.city_cards += self.game_state.card_manager.draw_city_cards()
        self.game_state.draw_infection_cards_and_place_cubes()
