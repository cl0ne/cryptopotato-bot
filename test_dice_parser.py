import unittest
from unittest import mock

from dice_parser import Dice, ParseError, ValueRangeError


class DiceParserTest(unittest.TestCase):
    def test_basic_notation(self):
        for roll_str, expected in (
            ('1d6', (1, 6)),
            ('d6', (1, 6)),
            ('d5', (1, 5)),
            ('5d1', (5, 1))
        ):
            with self.subTest(roll_str=roll_str):
                self.assertEqual(self._DiceVars(Dice.parse(roll_str)), expected)

        for roll_str in (
            'd', '1d',
            '-1d', '-1d6', 'd+6', '1d-6', '-6d-1'
        ):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ParseError, Dice.parse, roll_str)

        for roll_str in ('0d6', '1d0', 'd0', '0d0'):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ValueRangeError, Dice.parse, roll_str)

    def test_init(self):
        for rolls, sides in (
            (1, 1),
            (1, 6),
            (1, 10),
            (100, 6),
            (100, 1),
            (1, 120),
            (100, 120)
        ):
            with self.subTest(rolls=rolls, sides=sides):
                d = Dice(rolls, sides)
                self.assertEqual(d.rolls, rolls)
                self.assertEqual(d.sides, sides)

        for rolls, sides in (
            (0, 0),
            (0, 6),
            (1, 0),
            
            (-1, 6),
            (-1, -6),
            (1, -6),

            (1, 121),
            (100, 121),
            (120, 120),
            (120, 6),
            (120, 100)
        ):
            with self.subTest(rolls=rolls, sides=sides):
                self.assertRaises(ValueRangeError, Dice, rolls, sides)

    @mock.patch('random.randint', return_value=1)
    def test_get_result(self, randint):
        two_standard = Dice(3, 6)
        expected_calls = [mock.call(1, 6)] * 3
        
        for item_limit, expected_total, expected_rolls, expected_was_limited in (
                (None, 3, [1, 1, 1], False),
                (0, 3, [], True),
                (1, 3, [1], True),
                (2, 3, [1, 1], True),
                (3, 3, [1, 1, 1], False),
                (10, 3, [1, 1, 1], False)
        ):
            with self.subTest(item_limit=item_limit):
                roll_total, single_rolls, was_limited = two_standard.get_result(item_limit)
                randint.assert_has_calls(expected_calls)
                self.assertEqual(roll_total, expected_total)
                self.assertEqual(single_rolls, expected_rolls)
                self.assertEqual(was_limited, expected_was_limited)

        self.assertRaises(ValueError, two_standard.get_result, -1)
        self.assertRaises(ValueError, two_standard.get_result, -3)
    
    @staticmethod
    def _DiceVars(dice):
        return dice.rolls, dice.sides


if __name__ == '__main__':
    unittest.main()
