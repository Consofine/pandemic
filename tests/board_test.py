import sys
sys.path.append('..')
import unittest
from board import *
from constants import *


class TestGameMethods(unittest.TestCase):
    def test_game_init(self):
        game = Game(3)
        self.assertEqual(game.outbreak_count, 0)
        self.assertFalse(game.disease_cured[BLUE])
        self.assertFalse(game.disease_eradicated[GREY])
        self.assertEqual(game.diseases_remaining[RED], DISEASE_CUBE_LIMIT)
        self.assertEqual(game.infection_state.level, 1)
