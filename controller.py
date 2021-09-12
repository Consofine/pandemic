import jsonpickle
import json
from board import Board
from typing import List


class Serializer:
    @classmethod
    def load_board(self, id: str):
        """
        Class method for deserializing the game object from a json file
        Returns:
            board_object - Board object holding all information needed to play game
        """
        with open("game-{}.json".format(id), "r") as f:
            board_object = jsonpickle.decode(f.read())
        return board_object

    @classmethod
    def save_board(self, board: Board, id: str):
        """
        Class method for serializing board object to a json file
        Args:
            board_object - Board object holding all information needed to play game
        """
        with open("game-{}.json".format(id), "w+") as f:
            f.write(jsonpickle.encode(board, make_refs=False))

    @classmethod
    def print_board(self, board: Board) -> str:
        """
        Convenience method for turning a Board object into a JSON string
        which we can then send to the clients.
        """
        return json.dumps(board, default=lambda x: x.__dict__)


class Controller:
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
        b = Serializer.load_board(game_id)
        if "action" in msg:
            b.take_action(msg)
        Serializer.save_board(b, game_id)
        return Serializer.print_board(b)
