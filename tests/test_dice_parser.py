import itertools
import unittest
from unittest import mock

from devpotato_bot.dice_parser import Dice, ParseError, ValueRangeError, ResultsKeepStrategy, RollResult


class ResultsKeepStrategyMock:
    def __init__(self, total, discard):
        self._expected_total = total
        self._discarded_default = discard

    def get_discarded_default(self, _):
        return self._discarded_default

    def apply(self, results) -> int:
        if ResultsKeepStrategyMock.DEFAULT is self:
            print('apply')
        # ensure that actual strategy gets own copy of items
        results.clear()
        return self._expected_total


ResultsKeepStrategyMock.DEFAULT = ResultsKeepStrategyMock(-1, object())


class DiceTest(unittest.TestCase):
    def test_invalid_patterns(self):
        for roll_str in (
                'd', '1d', '-1d', '-1d6', 'd6+', 'd6-',
                'd+6', '1d-6', '-6d-1', 'd6-+6', 'd6+-6', 'd6-+-6', 'd6+d6',
                '%d', '1%d', '-%1d', '-1%d6', '-1d%', 'd%%', '2d%%',
                'd6L', 'd6H', 'dH1', 'dL1', 'd6L-1', 'd6H-1'
        ):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ParseError, Dice.parse, roll_str)

        for roll_str in ('0d6', '1d0', 'd0', '0d0', '0d%'):
            with self.subTest(roll_str=roll_str):
                self.assertRaises(ValueRangeError, Dice.parse, roll_str)

    def test_valid_patterns(self):
        roll_counts = [('', 1), ('1', 1), ('2', 2), ('10', 10), ('05', 5)]
        side_counts = [
            ('d6', 6), ('d20', 20),
            ('d%', 100), ('d100', 100),
            ('d1', 1), ('d2', 2), ('d03', 3)
        ]
        modifiers = [
            ('', 0), ('+0', 0),
            ('+1', 1), ('-1', -1),
            ('+05', 5), ('-05', -5)
        ]
        discards = itertools.chain(
            [('', (0, False, False))],
            (
                (f'{prefix}{t}{count}', (count, prefix != '-', t == 'L'))
                for prefix, t, count
                in itertools.product(['', '+', '-'], 'LH', [0, 1, 2, 10, 20])
            )
        )
        for i in itertools.product(roll_counts, side_counts, discards, modifiers):
            roll_str, expected_vars = zip(*i)
            roll_str = ''.join(roll_str)
            with self.subTest(roll_str=roll_str):
                rolls, sides, discard_vars, modifier = expected_vars
                d = Dice.parse(roll_str)
                self.assertEqual(d.sides, sides)
                self.assertEqual(d.rolls, rolls)
                self.assertEqual(d.modifier, modifier)

                discard_count, discard_keep, discard_lowest = discard_vars
                self.assertEqual(d.discard_strategy.count, min(discard_count, rolls))
                self.assertEqual(d.discard_strategy.keep, discard_keep)
                self.assertEqual(d.discard_strategy.lowest, discard_lowest)

    def test_init(self):
        self.assertEqual(Dice(1, 6).modifier, 0)
        self.assertEqual(Dice(1, 6, modifier=None).modifier, 0)
        self.assertEqual(Dice(1, 6).discard_strategy, ResultsKeepStrategy.DEFAULT)

        invalid_roll_counts = itertools.product(
            (-1, 0, Dice.ROLL_LIMIT + 1),
            (-1, 0, 6, 100, Dice.BIGGEST_DICE, Dice.BIGGEST_DICE + 1)
        )
        invalid_sides = itertools.product(
            (1, 10, Dice.ROLL_LIMIT),
            (-1, 0, Dice.BIGGEST_DICE + 1)
        )
        for rolls, sides in itertools.chain(invalid_roll_counts, invalid_sides):
            with self.subTest(rolls=rolls, sides=sides):
                self.assertRaises(ValueRangeError, Dice, rolls, sides)

    @mock.patch('random.randint')
    def test_get_result(self, randint):
        discard_strategy = ResultsKeepStrategyMock(1337, discard=object())
        for (roll_count, sides), modifier in itertools.product(
                [(1, 1), (1, 6), (10, 20)],
                [0, -1, +1]
        ):
            with self.subTest(rolls=roll_count, sides=sides, modifier=modifier):
                d = Dice(roll_count, sides, modifier=modifier, discard_strategy=discard_strategy)
                expected_calls = [mock.call(1, sides)] * roll_count
                for item_limit in (
                        None, 0, 1, roll_count - 1, roll_count, roll_count + 1, roll_count + 20
                ):
                    randint.side_effect = range(roll_count)
                    with self.subTest(item_limit=item_limit):
                        roll_total, single_rolls, was_limited = d.get_results(item_limit)
                        randint.assert_has_calls(expected_calls)
                        self.assertEqual(randint.call_count, roll_count)
                        self.assertEqual(roll_total, discard_strategy._expected_total + modifier)

                        should_limit = item_limit is not None and roll_count > item_limit
                        self.assertEqual(was_limited, should_limit)

                        expected_rolls = range(item_limit if should_limit else roll_count)
                        self.assertTrue(all(
                            r.value == e
                            for r, e in itertools.zip_longest(single_rolls, expected_rolls)
                        ))
                        self.assertTrue(all(
                            r.is_discarded is discard_strategy._discarded_default
                            for r in single_rolls
                        ))
                    randint.reset_mock()

                for item_limit in (-1, -roll_count, -roll_count-1):
                    with self.subTest(item_limit=item_limit):
                        self.assertRaises(ValueError, d.get_results, item_limit)
                        randint.assert_not_called()
                    randint.reset_mock()


class ResultsKeepStrategyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ordered = tuple(range(1, 11))
        shuffled = list(ordered)
        import random
        random.seed(1024)
        random.shuffle(shuffled)
        random_items = tuple(random.randint(1, 10) for _ in range(10))
        cls.items_pool = (
            ('reversed', tuple(reversed(ordered)), ordered),
            ('shuffled', tuple(shuffled), ordered),
            ('random', random_items, tuple(sorted(random_items)))
        )

    def test_init(self):
        for count, keep, use_lowest in itertools.product(
                (-1, -2), (True, False), (True, False)
        ):
            self.assertRaises(ValueError, ResultsKeepStrategy, count=count, keep=keep, lowest=use_lowest)

    def test_apply(self):
        for item_set_name, items, ordered in self.items_pool:
            item_count = len(items)
            for discard_count, keep, use_lowest in itertools.product(
                    range(0, item_count+2),
                    (True, False),
                    (True, False)
            ):
                with self.subTest(item_set=item_set_name, discard_count=discard_count, keep=keep, use_lowest=use_lowest):
                    s = ResultsKeepStrategy(discard_count, keep=keep, lowest=use_lowest)
                    discard_by_default = s.get_discarded_default(item_count)
                    self.assertEqual(discard_by_default, (discard_count >= item_count//2) != keep)

                    roll_results = [RollResult(i, discard_by_default) for i in items]
                    total = s.apply(roll_results)
                    roll_results.sort(key=lambda r: (r.value, r.is_discarded == (keep == use_lowest)))

                    self.assertTrue(all(
                        r.value == i for r, i in itertools.zip_longest(roll_results, ordered)
                    ))

                    keep_lowest = (keep == use_lowest)
                    lowest_count = discard_count if use_lowest else max(0, item_count-discard_count)
                    kept_slice = ((0, lowest_count) if keep_lowest else (lowest_count, None))
                    self.assertEqual(total, sum(itertools.islice(ordered, *kept_slice)))
                    self.assertTrue(all(
                        r.is_discarded == ((i < lowest_count) != keep_lowest)
                        for i, r in enumerate(roll_results)
                    ))


if __name__ == '__main__':
    unittest.main()
