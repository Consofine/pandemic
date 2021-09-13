from enum import Enum
from constants import *


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


class AbilityList(Enum):
    """
    Enum for holding non-standard actions, such as Role-specific abilities, card
    abilities, and miscellaneous actions like discarding cards and ending turns.
    """
    discard = DISCARD
    end_turn = END_TURN
