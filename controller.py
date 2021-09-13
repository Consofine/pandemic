import json
import time
import pickle
from typing import List
from board import Board, CityCard, City, Player
from enums import ActionList, AbilityList
from constants import ACTION, ABILITY
from custom_exceptions import InvalidOperationError


class Serializer:
    @classmethod
    def load_board(self, id: str):
        """
        Class method for deserializing the game object from a json file
        Returns:
            board_object - Board object holding all information needed to play game
        """
        with open("game-{}.pickle".format(id), "rb") as f:
            #board_object = jsonpickle.decode(f.read())
            board_object = pickle.load(f)
        return board_object

    @classmethod
    def save_board(self, board: Board, id: str):
        """
        Class method for serializing board object to a json file
        Args:
            board_object - Board object holding all information needed to play game
        """
        with open("game-{}.pickle".format(id), "wb+") as f:
            #f.write(jsonpickle.encode(board, make_refs=False))
            pickle.dump(board, f)

    @classmethod
    def print_board(self, board: Board, error: bool = None) -> str:
        """
        Convenience method for turning a Board object into a JSON string
        which we can then send to the clients.
        """
        return json.dumps({"board": board, "error": error}, default=lambda x: x.__dict__)


class Controller:
    def __init__(self):
        """
        Sets up mappings for message types to methods and arguments.
        """
        self.action_mappings = {
            ActionList.move_adjacent: Board.move_adjacent,
            ActionList.move_direct_flight: Board.move_direct_flight,
            ActionList.move_charter_flight: Board.move_charter_flight,
            ActionList.move_shuttle_flight: Board.move_shuttle_flight,
            ActionList.build_research_station: Board.build_research_station,
            ActionList.treat_disease: Board.treat_disease,
            ActionList.share_knowledge: Board.share_knowledge,
            ActionList.discover_cure: Board.discover_cure,
            AbilityList.discard: Board.discard,
            AbilityList.end_turn: Board.move_to_next_player,
        }

        self.arg_mappings = {
            ActionList.move_adjacent: {"to_city": City},
            ActionList.move_direct_flight: {"city_card": CityCard},
            ActionList.move_charter_flight: {"city_card": CityCard, "to_city": City},
            ActionList.move_shuttle_flight: {"to_city": City},
            ActionList.build_research_station: {"city_card": CityCard},
            ActionList.treat_disease: {"color": str},
            ActionList.share_knowledge: {"city_card": CityCard, "player_to": Player, "player_from": Player},
            ActionList.discover_cure: {"city_cards": list([CityCard]), "color": str},
            AbilityList.discard: {"city_cards": list(
                [CityCard]), "player": Player},
            AbilityList.end_turn: {},
        }

    def init_board(self, game_id: str, player_ids: List[str], starting_city: str = None) -> str:
        """
        Create board object (which also does its own initialization). Serialize board, then return board
        object (to send to clients).
        """
        if starting_city:
            b = Board(player_ids, starting_city)
        else:
            b = Board(player_ids)
        Serializer.save_board(b, game_id)
        return Serializer.print_board(b)

    def handle_input(self, game_id, msg) -> str:
        """
        Handle any incoming message from clients. This could be:
            -taking an action (making a move that counts towards a
                player's per-turn limit)
            -using an ability (e.g. putting down a research station in
                a city the player isn't in, which can be done outside
                of the player's turn)
            -miscellaneous (e.g. sending which cards to discard when a
                player has too many in their hand)

        Returns:
            str - JSON-dumped representation of the current board
        """
        print("msg: {}".format(msg))
        msg = json.loads(msg)
        start = time.time()
        b = Serializer.load_board(game_id)
        end = time.time()
        print("Load took {}.".format(end - start))
        start = time.time()
        error = None
        if ACTION in msg or ABILITY in msg:
            try:
                cmd_type = ACTION if ACTION in msg else ABILITY
                cmd = ActionList(msg[cmd_type]["name"])
                method = self.action_mappings[cmd]
                arg_keys = self.arg_mappings[cmd]
                args = [msg[cmd_type]["args"][key] for key in arg_keys.keys()]
                success = self.validate_keys(b, args, list(
                    arg_keys.values())) and method(b, *args)
                if not success:
                    raise InvalidOperationError("Action failed.")
                if cmd_type == ACTION:
                    b.dec_active_player_actions()
                    b.check_end_of_actions()
            except Exception as e:
                error = True
        end = time.time()
        print("Action took {}.".format(end - start))
        start = time.time()
        Serializer.save_board(b, game_id)
        end = time.time()
        print("Save took {}.".format(end - start))
        return Serializer.print_board(b, error)

    def validate_keys(self, board: Board, keys: List, types: List):
        try:
            for x in range(len(keys)):
                if types[x] == Player:
                    keys[x] = board.get_player(keys[x])
                elif types[x] == City:
                    keys[x] = board.get_city(keys[x])
                elif isinstance(types[x], list):
                    keys[x] = [types[x][0](element) for element in keys[x]]
                else:
                    keys[x] = types[x](keys[x])
        except ValueError:
            return False
        return True
