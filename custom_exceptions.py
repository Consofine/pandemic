class GameEndedError(Exception):
    """
    Custom error object for when the game ends
    """

    def __init__(self, message):
        super().__init__(message)


class InvalidOperationError(Exception):
    """
    Custom error object for general things that should't happen
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InvalidGametypeError(Exception):
    """
    Custom error object for when the wrong/invalid game type is passed
    Args:
        expected_obj - obj that we were supposed to be given
        given_obj - obj that we actually got
    """

    def __init___(self, expected_obj, given_obj):
        super().__init__("Invalid game type provided. Expected {} but given {}".format(
            type(expected_obj).__name__, type(given_obj).__name__))
