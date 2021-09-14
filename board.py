from typing import Any, Counter, List, Union, Dict
import random
import json
import functools
from custom_exceptions import GameEndedError, InvalidGametypeError, InvalidOperationError
from constants import *


class Role:
    """
    Used to represent specific power of each player
    """

    def __init__(self):
        self.power = None


class City:
    """
    Representing a board location and its state
    """
    outbreaks_occurred = 0

    def __init__(self, name: Union[str, 'City']):
        if isinstance(name, City):
            return
        if name not in CITY_LIST:
            raise ValueError("Invalid city name supplied to city constructor.")
        self.name: str = name
        self.color = CITY_LIST[name]
        self.disease_count: Dict[str, int] = dict.fromkeys(
            [RED, BLUE, YELLOW, GREY], 0)
        self.has_research_station: bool = False
        self.connected_cities: List[str] = []

    def __eq__(self, other):
        """
        (in)Equality based on whether cities share name
        """
        if isinstance(other, str):
            return self.name == other
        if not isinstance(other, City) and not isinstance(other, Card):
            return False
        return self.name == other.name and self.color == other.color

    def __str__(self):
        return "{}: {}. Connections to: {}".format(self.name, self.color, [self.connected_cities])

    def __repr__(self) -> str:
        return self.__str__()

    def set_connected_cities(self, cities: List[str]):
        """
        Stores list of cities as being adjacent to this
        Args:
            cities - list of cities that should be connected to this one
        """
        self.connected_cities = cities

    def add_single_disease(self, city_list: Dict[str, 'City'], color, prior_outbreaks: List[str] = []) -> bool:
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
        prior_outbreaks.append(self.name)
        self.trigger_outbreak(city_list, color, prior_outbreaks)
        return True

    def add_epidemic_disease(self, city_list: Dict[str, 'City'], color) -> bool:
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
        self.trigger_outbreak(city_list, color, [])
        return True

    def trigger_outbreak(self, city_list: Dict[str, 'City'], color, prior_outbreaks: List[str]) -> None:
        """
        Adds one disease cube of given color to each connected city. Prevents infinite loops / chaining
        back to cities that have already been hit, but allows for chaining otherwise
        Args:
            color - color of disease that is outbreaking
            prior_outbreaks - array to track cities that have been hit by this outbreak chain
        """
        City.outbreaks_occurred += 1
        for city_name in self.connected_cities:
            if city_name not in prior_outbreaks:
                city_list[city_name].add_single_disease(
                    city_list, color, prior_outbreaks)

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

    def treat_all_disease(self, color) -> bool:
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


class Card:
    """
    Parent class holding city name and color
    """

    def __init__(self, city_name: Union[str, 'Card']):
        if isinstance(city_name, Card):
            return
        if not city_name in CITY_LIST:
            raise ValueError(
                "Invalid name passed to Card constructor: {}".format(city_name))
        self.name = city_name
        self.color = CITY_LIST[city_name]

    def __eq__(self, other: object) -> bool:
        """
        (in)Equality based on whether cities share name
        """
        if not isinstance(other, City) and not isinstance(other, Card):
            return False
        return self.name == other.name and self.color == other.color

    def __str__(self) -> str:
        return "Card: {} - {}".format(self.name, self.color)

    def __repr__(self) -> str:
        return self.__str__()


class CityCard(Card):
    """
    Representing the type of card used to cure diseases and travel.
    """

    def __init__(self, city_name: Union[str, Card]):
        super().__init__(city_name)


class InfectionCard(Card):
    """
    Representing the type of card that is drawn at the end of each turn and used to
    place new infections in certain cities.
    """

    def __init__(self, city_name: Union[str, Card]):
        super().__init__(city_name)


class EpidemicCard:
    """
    Representing the type of card that is distributed throughout the infection card deck
    and, when drawn, triggers the placement of epidemic diseases on the bottom city in the
    infection card deck, as well as reshuffling of the infection card discard deck.
    """


class Player:
    """
    Represents one player (including location, powers, and state) from the game
    """

    def __init__(self, player_id: str, role: Role, starting_city: City):
        self.player_id = player_id
        self.role = role
        self.is_active = False
        self.actions_left = 0
        self.city_cards: List[CityCard] = []
        self.current_city = starting_city

    def __eq__(self, other: object):
        """
        Override the equality operator. Really only care about the id here, since no two players
        should have the same id.
        """
        if not isinstance(other, Player):
            return False
        return self.player_id == other.player_id

    def __str__(self):
        return "Player with ID {}. Active: {}, current city: {}".format(self.player_id, self.is_active, self.current_city)

    def move_adjacent(self, city: City) -> bool:
        """
        Move player to an adjacent City and decrements number of actions left.
        Args:
            city - City to move to
        Returns:
            bool - true if move is successful, false otherwise
        """
        if city in self.current_city.connected_cities:
            self.current_city = city
            return True
        return False

    def move_direct_flight(self, city: City) -> bool:
        """
        Move player to the city on the card being played.
        Args:
            city - City representing city to move to
        Returns:
            bool - True if move is successful, False otherwise
        """
        if city != self.current_city:
            self.current_city = city
            return True
        return False

    def move_charter_flight(self, cur_city_card: CityCard, dest_city: City) -> bool:
        """
        When player plays city card matching their current location, move them
        to any city they choose.
        Args:
            cur_city: City matching player's current location
            dest_city: City to which player is moving
        Returns:
            bool - true if move is successful, false otherwise
        """
        if cur_city_card not in self.city_cards:
            return False
        if dest_city != self.current_city and cur_city_card == self.current_city:
            self.current_city = dest_city
            return True
        return False

    def move_shuttle_flight(self, dest_city: City) -> bool:
        """
        Allows player to move from any city with a research station to any
        other city with a research station
        Args:
            dest_city - City to which player is moving
        Returns:
            bool - true if move is successful, false otherwise
        """
        if dest_city != self.current_city and self.current_city.has_research_station and dest_city.has_research_station:
            self.current_city = dest_city
            return True
        return False

    def give_knowledge(self, city_card: CityCard, other_player: 'Player') -> bool:
        """
        If city_card is in this player's city card deck, gives that card to other_player.
        Args:
            city_card - CityCard that we want to give to the other player
            other_player - Player to whom we want to give our card
        Returns:
            bool - true if card successfully given, false otherwise
        """
        if other_player.current_city != self.current_city or city_card != self.current_city:
            return False
        if self.subtract_card(city_card):
            if other_player.add_card(city_card):
                return True
            else:
                # we just removed this, but couldn't give it to other player.
                # add back in so it's not lost.
                self.add_card(city_card)
        return False

    def add_card(self, city_card: CityCard) -> bool:
        """
        Adds a given card to this player's hand. 
        TODO: add in logic for handling discarding. Currently, this just doesn't let a 
        player take another card if they have a full hand.
        """
        if len(self.city_cards) < MAX_HAND_COUNT and not city_card in self.city_cards:
            self.city_cards.append(city_card)
            return True
        return False

    def subtract_card(self, city_card: CityCard) -> bool:
        """
        Take a given card from this player's hand. 
        Args:
            city_card - CityCard we want to subtract from this player's hand
        Returns:
            bool - true if card successfully taken, false otherwise
        """
        try:
            self.city_cards.remove(city_card)
            return True
        except ValueError:
            return False

    def can_discover_cure(self, color: str, city_cards: List[CityCard] = []) -> bool:
        """
        Checks if player is at a city with a research station and 
        has enough city cards of given color to cure that disease.
        Args:
            color - string representing color of disease we want to cure
        Returns:
            bool - true if we can discover a cure, false otherwise
        """
        if not city_cards:
            city_cards = self.city_cards

        if not self.current_city.has_research_station:
            return False

        def color_matches(city_card: CityCard) -> int:
            nonlocal color
            return 1 if city_card.color == color else 0

        has_enough_cards = sum(
            list(map(color_matches, city_cards))) >= CURE_COUNT
        cards_in_hand = functools.reduce(lambda a, b: a and b, [
                                         city_card in self.city_cards for city_card in city_cards])
        return has_enough_cards and cards_in_hand

    def discover_cure(self, color: str, city_cards: List[CityCard]) -> None:
        """
        Discover cure using given city_cards by removing those cards from this
        player's hand. Note that this should only be called after checking
        can_discover_cure.
        """
        # check if we can discover cure with any color in the set of city cards
        if not city_cards or not self.can_discover_cure(color, city_cards):
            raise InvalidOperationError(
                "Tried to cure disease without enough cards")
        # if we have more cards than we need (shouldn't happen), use first 5
        if len(city_cards) > CURE_COUNT:
            tmp = [c for c in city_cards if c.color == color]
            city_cards = tmp[:CURE_COUNT]
        for city_card in city_cards:
            self.subtract_card(city_card)

    def build_research_station(self, city_card: CityCard) -> bool:
        """
        Helper method for checking if this player can build a research station in their
        current city, using the given city card. Player's location must match card, and
        there must not already be a research station in this city.
        Removes the given card from the user's hand if they can build the research station.
        Returns:
            bool - True if the user can build a research station, otherwise False
        """
        if city_card not in self.city_cards or city_card != self.current_city or self.current_city.has_research_station:
            return False
        if self.subtract_card(city_card):
            if self.current_city.add_research_station():
                return True
            # add card back in, since we can't actually build (shouldn't happen)
            self.add_card(city_card)
        return False

    def has_actions_left(self) -> bool:
        """
        Checks if this player has more actions left in their turn.
        Returns:
            bool - true if player has more actions, false otherwise
        """
        return self.actions_left > 0

    def dec_actions_left(self):
        """
        Decrements this player's number of actions left in their turn.
        Doesn't raise any errors or do checking because this should
        only be called after explicitly calling has_actions_left()
        """
        self.actions_left -= 1

    def make_active(self):
        """
        Make this player active. Doesn't handle de-activating all other players.
        """
        self.is_active = True
        self.actions_left = MAX_ACTIONS


class CardManager:
    """
    Object for storing CityCard deck and InfectionCard deck, along with methods for accessing
    """

    def __init__(self, num_epidemic_cards: int = MIN_NUM_EPIDEMIC_CARDS):
        self.number_of_epidemic_cards = num_epidemic_cards
        self.city_card_deck: List = self.init_city_cards(num_epidemic_cards)
        self.city_card_discard: List = []
        self.infection_card_deck: List = self.init_infection_cards()
        self.infection_card_discard: List = []

    def init_city_cards(self, num_epidemic_cards: int = MIN_NUM_EPIDEMIC_CARDS) -> List[CityCard]:
        """
        Creates a deck of CityCards using the city_list constant
        Returns:
            [CityCard | EpidemicCard] - deck of CityCards and EpidemicCards for game
        """
        city_cards: List = [CityCard(c)
                            for c in CITY_LIST.keys()]
        city_cards.extend([EpidemicCard()] * num_epidemic_cards)
        random.shuffle(city_cards)
        return city_cards

    def init_infection_cards(self) -> List[InfectionCard]:
        """
        Creates a deck of InfectionCards using the city_list constant
        Returns:
            [InfectionCard] - deck of InfectionCards for game
        """
        infection_cards = [InfectionCard(c)
                           for c in CITY_LIST.keys()]
        random.shuffle(infection_cards)
        return infection_cards

    def handle_epidemic(self) -> InfectionCard:
        """
        After an epidemic card is drawn from the city card pile, we need to:
        * draw the bottom infection card from the deck and add an epidemic there (3 disease cubes)
        * shuffle that infection card with the infection discards and return to top of infection deck

        Returns:
            InfectionCard - Card for city that we'll need to add an epidemic disease to
        """
        bottom_card = self.draw_bottom_infection_card()
        self.shuffle_and_replace_infection_cards()
        return bottom_card

    def draw_city_cards(self) -> List[CityCard]:
        """
        Removes 2 CityCards from the top of the deck. If there aren't 2 CityCards remaining, throws error.
        If one of the drawn cards is an Epidemic Card, returns (potentially) early and handles shuffling of
        infection cards.
        Returns:
            CityCards - array of 2 city cards or epidemic cards
        Raises:
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
        # not sure if this is game over, but just reshuffle and keep going
        if len(self.infection_card_deck) < number:
            # take however many are left, then shuffle
            infection_cards = self.infection_card_deck
            self.infection_card_deck = self.infection_card_discard
            random.shuffle(self.infection_card_deck)
            self.infection_card_discard = []
            num_left = number - len(infection_cards)
            infection_cards.extend(self.infection_card_deck[0:num_left])
            self.infection_card_discard[:0] = infection_cards
            del self.infection_card_deck[0:num_left]
        else:
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

    def increase_outbreak_count(self) -> None:
        """
        Increase the outbreak level. If we hit the max number of outbreaks, raise GameEndedError
        """
        self.outbreak_count += 1
        if self.outbreak_count >= MAX_OUTBREAK_COUNT:
            raise GameEndedError("Hit limit for outbreaks")


class DiseaseManager:
    """
    Object for holding data about remaining diseases and disease statuses(cured / eradicated)
    """

    def __init__(self):
        self.diseases_cured: Dict[str, bool] = dict.fromkeys(COLORS, False)
        self.diseases_eradicated: Dict[str,
                                       bool] = dict.fromkeys(COLORS, False)
        self.diseases_remaining: Dict[str, int] = dict.fromkeys(
            COLORS, DISEASE_CUBE_LIMIT)

    def update_disease_counts(self, cities_list: List[City]) -> None:
        """
        Update the disease metrics tracked in this class. Loops through all cities and gets sums,
        then updates the amount of disease remaining. If no more cubes for a given disease, ends game.
        """
        self.diseases_remaining = dict.fromkeys(COLORS, DISEASE_CUBE_LIMIT)
        for city in cities_list:
            for color in COLORS:
                if city.disease_count[color] > self.diseases_remaining[color]:
                    raise GameEndedError("Ran out of disease cubes.")
                self.diseases_remaining[color] -= city.disease_count[color]

    def get_remaining_diseases(self, color: str = None) -> Union[Dict[str, int], int]:
        """
        Returns the dict of remaining diseases, or the count remaining for a specific disease color
        if provided
        Args:
            color(opt) - string representing color of disease
        """
        if color is not None:
            return self.diseases_remaining[color]
        return self.diseases_remaining

    def is_cured(self, color: str) -> bool:
        """
        Check if a disease has been cured already
        Args:
            color - string representing color of disease being checked
        Returns:
            bool - True if disease is cured, else false
        """
        return self.diseases_cured[color]

    def is_eradicated(self, color: str) -> bool:
        """
        Check if a disease has been eradicated already
        Args:
            color - string representing color of disease being checked
        Returns:
            bool - True if disease is eradicated, else false
        """
        return self.diseases_eradicated[color]

    def cure_disease(self, color: str) -> None:
        """
        Set a disease's status to cured.
        Args:
            color - string representing color of disease being cured
        """
        self.diseases_cured[color] = True

    def eradicate_disease(self, color: str) -> None:
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


class Board:
    """
    Holds game state, list of cities, and players (with their positions)
    etc
    """

    def __init__(self, player_ids: List[str], starting_city: str = STARTING_CITY) -> None:
        # set up game state
        self.infection_manager: InfectionManager = InfectionManager()
        self.disease_manager: DiseaseManager = DiseaseManager()
        self.card_manager: CardManager = CardManager()
        self.cities: Dict[str, City] = self.init_cities(starting_city)
        self.player_ids = player_ids
        # create player list and set active player
        self.players: Dict[str, Player] = {p: Player(p, Role(), self.get_city(starting_city))
                                           for p in player_ids}
        self.set_active_player(self.players[player_ids[0]])

    def set_active_player(self, player: Union[str, Player]) -> None:
        """
        Set the active player to be the given player object. Also, set all other
        players' active statuses to False, and set this player's active status to True.
        Args:
            Player - a Player object representing the new active player
        """
        for p in self.players.values():
            if p == player:
                self.active_player = p
                p.make_active()
            else:
                p.is_active = False
                p.actions_left = 0

    @classmethod
    def init_cities(self, starting_city: str) -> Dict[str, City]:
        """
        Using cities and connected cities information from constants file,
        creates a dict holding all cities with all of their related data
        Returns: 
            cities - dict associating city names to city objects for all 48 cities
        """
        cities = {c: City(c) for c in CITY_LIST.keys()}
        for city in cities.values():
            city.set_connected_cities(CITY_CONNECTIONS[city.name])
        cities[starting_city].add_research_station()
        return cities

    def move_adjacent(self, to_city: City):
        """
        Move to a neighboring city (from active player's current city)
        """
        return self.active_player.move_adjacent(to_city)

    def move_direct_flight(self, city_card: CityCard):
        """
        Play a city card and move to the city matching that card.
        """
        city = self.get_city(city_card.name)
        return self.active_player.move_direct_flight(city)

    def move_charter_flight(self, city_card: CityCard, to_city: City):
        """
        Play a city card matching the active player's current city and fly to
        anywhere you want.
        """
        cur_city = CityCard(self.get_city(city_card.name).name)
        return self.active_player.move_charter_flight(cur_city, to_city)

    def move_shuttle_flight(self, to_city: City):
        """
        Move from one city with a research station (active player's current city)
        to another city with a research station.
        """
        return self.active_player.move_shuttle_flight(to_city)

    def build_research_station(self, city_card: CityCard):
        """
        Build a research station in the active player's current city, or 
        in the city corresponding to the supplied city name if given. Building
        a research station outside of the active player's current city is a 
        special power-up.
        TODO: handle special case for non-active city
        """
        return self.active_player.build_research_station(city_card)

    def treat_disease(self, color: str):
        """
        Treat disease in the active player's current city. If this disease
        has been cured, treat all disease cubes of the given color. Else treat
        one disease cube.
        """
        if color not in COLORS:
            return False
        if self.disease_manager.is_cured(color):
            success = self.active_player.current_city.treat_all_disease(color)
            if not self.disease_manager.diseases_remaining[color]:
                self.disease_manager.eradicate_disease(color)
            return success
        return self.active_player.current_city.treat_single_disease(color)

    def share_knowledge(self, city_card: CityCard, player_to: Player, player_from: Player):
        """
        Share knowledge, giving a card from player_from to player_to.
        """
        if not (player_to == self.active_player or player_from == self.active_player):
            return False
        return player_from.give_knowledge(city_card, player_to)

    def discover_cure(self, city_cards: List[CityCard], color: str) -> bool:
        """
        If active player has all the provided city cards and there are enough
        of them to cure a disease of the given color and the active player is 
        in a city with a research station, cure disease.
        """
        if self.active_player.can_discover_cure(color, city_cards):
            if not self.disease_manager.is_cured(color):
                self.disease_manager.cure_disease(color)
                self.active_player.discover_cure(color, city_cards)
                return True
        return False

    def move_to_next_player(self):
        """
        At the end of the current player's turn, make the next player active.
        """
        next_player_id = self.player_ids[(self.player_ids.index(
            self.active_player.player_id) + 1) % len(self.player_ids)]
        self.set_active_player(self.players[next_player_id])

    def draw_city_cards(self) -> List[CityCard]:
        """
        After a player's actions have all been used/turn has ended, draw two city cards for
        them. Handle epidemic if it occurs. After epidemic occurs, update disease counts- a way
        to also check if the game has ended.
        """
        cards = self.card_manager.draw_city_cards()
        city_cards = []
        for card in cards:
            if not isinstance(card, EpidemicCard):
                city_cards.append(card)
                continue
            self.infection_manager.increase_level()
            bottom_card = self.card_manager.handle_epidemic()
            self.cities[bottom_card.name].add_epidemic_disease(
                self.cities, bottom_card.color)
            self.disease_manager.update_disease_counts(
                list(self.cities.values()))
        for _ in range(City.outbreaks_occurred):
            self.infection_manager.increase_outbreak_count()
        City.outbreaks_occurred = 0
        return city_cards

    def draw_infection_cards_and_place_cubes(self):
        """
        At the end of the turn, draw the number of infection cards corresponding to
        InfectionManager.rate. Place cubes as needed. If we hit an epidemic card, handle
        that as well.
        """
        infection_cards = self.card_manager.draw_infection_cards(
            self.infection_manager.rate)
        for ic in infection_cards:
            self.cities[ic.name].add_single_disease(self.cities, ic.color)
        for _ in range(City.outbreaks_occurred):
            self.infection_manager.increase_outbreak_count()
        self.disease_manager.update_disease_counts(
            list(self.cities.values()))
        City.outbreaks_occurred = 0

    def dec_active_player_actions(self):
        """
        Calls into active player's dec_actions_left method.
        """
        self.active_player.dec_actions_left()

    def discard(self, city_cards: List[CityCard], player: Player):
        """
        Discard the given city cards from the given player's hand, if
        they possess these cards already.
        """
        error = False
        for c in city_cards:
            if not player.subtract_card(c):
                error = True
        return error

    def check_end_of_actions(self):
        """
        Draw city cards and give them to the active player. Draw
        infection cards and place disease cubes on respective cities.
        Handle epidemics if one occurs while drawing city cards.
        TODO: handle case where user has too many cards
        """
        if self.active_player.has_actions_left():
            return
        self.active_player.city_cards += self.card_manager.draw_city_cards()
        self.draw_infection_cards_and_place_cubes()
        # if len(self.active_player.city_cards) <= MAX_HAND_COUNT:
        self.move_to_next_player()

    def get_city(self, city_name: Union[str, City]) -> City:
        """
        Get City object from the given city name (i.e. probably the city's name field).
        """
        if isinstance(city_name, City):
            return city_name
        if not city_name in self.cities:
            raise InvalidOperationError("Invalid city name.")
        return self.cities[city_name]

    def get_player(self, player_id: Union[str, Player]) -> Player:
        """
        Get player object from the given player id (i.e. probably the player's player_id field).
        """
        if isinstance(player_id, Player):
            return player_id
        if not player_id in self.players.keys():
            raise InvalidOperationError("Invalid player id.")
        return self.players[player_id]
