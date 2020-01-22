import unittest
from unittest import mock

from devpotato_bot.dice_parser import Dice, ParseError, ValueRangeError


class DiceParserTest(unittest.TestCase):
    @staticmethod
    def _DiceVars(dice):
        return dice.rolls, dice.sides, dice.modifier
    
    def test_basic_notation(self):
        for roll_str, expected in (
            ('1d6', (1, 6, 0)),
            ('d6', (1, 6, 0)),
            ('d5', (1, 5, 0)),
            ('5d1', (5, 1, 0))
        ):
            with self.subTest(roll_str=roll_str):
                self.assertEqual(self._DiceVars(Dice.parse(roll_str)), expected)

        for roll_str in ('d', '1d', '-1d', '-1d6'):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ParseError, Dice.parse, roll_str)

        for roll_str in ('0d6', '1d0', 'd0', '0d0'):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ValueRangeError, Dice.parse, roll_str)
    
    def test_modifier(self):
        for roll_str, expected in (
            ('d6-5', (1, 6, -5)),
            ('d6+5', (1, 6, 5)),
            ('d6+0', (1, 6, 0)),
            ('2d10-1', (2, 10, -1))
        ):
            with self.subTest(roll_str=roll_str):
                self.assertEqual(self._DiceVars(Dice.parse(roll_str)), expected)

        for roll_str in ('d+6', '1d-6', '-6d-1', 'd6+', 'd6-', 'd6-+6', 'd6+-6', 'd6-+-6', 'd6+d6'):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ParseError, Dice.parse, roll_str)

    def test_percentile_dice(self):
        for roll_str, expected in (
            ('d%',      (1, 100, 0)),
            ('d%-5',    (1, 100, -5)),
            ('d%+5',    (1, 100, 5)),
            ('d%+0',    (1, 100, 0)),
            ('2d%-1',   (2, 100, -1)),
            ('2d%+1',   (2, 100, 1))
        ):
            with self.subTest(roll_str=roll_str):
                self.assertEqual(self._DiceVars(Dice.parse(roll_str)), expected)

        for roll_str in ('%d', '1%d', '-%1d', '-1%d6', '-1d%', 'd%%', '2d%%'):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ParseError, Dice.parse, roll_str)

        self.assertRaises(ValueRangeError, Dice.parse, '0d%')

    def test_init(self):
        for rolls, sides, modifier in (
            (1, 1, 0),
            (1, 6, 0),
            (1, 10, 0),
            (100, 6, 0),
            (100, 1, 0),
            (1, 120, 0),
            (100, 120, 0)
        ):
            with self.subTest(rolls=rolls, sides=sides):
                d = Dice(rolls, sides)
                self.assertEqual(self._DiceVars(d), (rolls, sides, modifier))
            
            with self.subTest(rolls=rolls, sides=sides, modifier=None):
                d = Dice(rolls, sides, None)
                self.assertEqual(self._DiceVars(d), (rolls, sides, modifier))
            
            with self.subTest(rolls=rolls, sides=sides, modifier=modifier):
                d = Dice(rolls, sides, modifier)
                self.assertEqual(self._DiceVars(d), (rolls, sides, modifier))
        
        for rolls, sides, modifier in (
            (1, 1, -1),
            (1, 1, 1),
            (1, 6, 6),
            (1, 6, -6)
        ):
            with self.subTest(rolls=rolls, sides=sides, modifier=modifier):
                d = Dice(rolls, sides, modifier)
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
        for roll_count, sides, modifier in (
            (1, 2, 0), (3, 6, 0), (3, 6, -1), (3, 6, +1), (5, 10, -10), (5, 10, +10),
            (1, 100, 0), (5, 100, -5), (10, 100, 0), (2, 100, 10)
        ):
            with self.subTest(rolls=roll_count, sides=sides, modifier=modifier):
                d = Dice(roll_count, sides, modifier)
                expected_calls = [mock.call(1, sides)] * roll_count
                expected_total = roll_count + modifier
                expected_rolls = [1] * roll_count
                for item_limit in (
                    None, 0, 1, roll_count - 1, roll_count, roll_count + 1, roll_count + 20
                ):
                    with self.subTest(item_limit=item_limit):
                        roll_total, single_rolls, was_limited = d.get_result(item_limit)
                        randint.assert_has_calls(expected_calls)
                        self.assertEqual(randint.call_count, roll_count)
                        self.assertEqual(roll_total, expected_total)
                        
                        limit_is_set = item_limit is not None and roll_count > item_limit
                        self.assertEqual(was_limited, limit_is_set)
                        roll_subset = expected_rolls[:(item_limit if limit_is_set else roll_count)]
                        self.assertSequenceEqual(single_rolls, roll_subset)
                    randint.reset_mock()
                
                for item_limit in (-1, -roll_count, -roll_count-1):
                    with self.subTest(item_limit=item_limit):
                        self.assertRaises(ValueError, d.get_result, item_limit)
                        randint.assert_not_called()
                    randint.reset_mock()


if __name__ == '__main__':
    unittest.main()
