import itertools
import random
import re
from typing import List, Tuple, Optional

from devpotato_bot.quickselect import select


class ParseError(Exception):
    def __init__(self):
        super().__init__('Roll is not in dice notation')


class ValueRangeError(ValueError):
    def __init__(self, arg_name, value, allowed_range: Tuple[Optional[int], Optional[int]]):
        self.arg_name = arg_name
        self.value = value
        self.allowed_range = allowed_range
        super().__init__({
            'arg_name': arg_name,
            'value': value,
            'allowed_range': allowed_range
        })


class RollResult:
    def __init__(self, value, is_discarded=False):
        self.value = value
        self.is_discarded = is_discarded


class ResultsKeepStrategy:
    def __init__(self, count, *, keep, lowest):
        if count < 0:
            raise ValueError('count should be non-negative')
        self.count = count
        self.keep = keep
        self.lowest = lowest

    def get_discarded_default(self, roll_count):
        # self.keep if self.count < roll_count/2 else not self.keep
        return self.keep == (self.count < roll_count - self.count)

    @staticmethod
    def _compare_lowest(a: RollResult, b: RollResult):
        return a.value < b.value

    @staticmethod
    def _compare_highest(a: RollResult, b: RollResult):
        return a.value > b.value

    def apply(self, results: List[RollResult]) -> int:
        remaining_items = max(0, len(results) - self.count)
        # Always select lower part
        if self.count < remaining_items:
            count = self.count
            discard_selected = not self.keep
            select_lowest = self.lowest
        else:
            count = remaining_items
            discard_selected = self.keep
            select_lowest = not self.lowest
        comparator = self._compare_lowest if select_lowest else self._compare_highest
        select(results, count, compare=comparator)
        for r in itertools.islice(results, count):
            r.is_discarded = discard_selected
        kept_range = (count, None) if discard_selected else (0, count)
        return sum(r.value for r in itertools.islice(results, *kept_range))


# default strategy is "discard none"
ResultsKeepStrategy.DEFAULT = ResultsKeepStrategy(0, keep=False, lowest=False)


class Dice:
    __regex = re.compile(
        r'(?P<rolls>\d+)?'
        r'd'
        r'(?P<sides>\d+|%)'
        r'(?:(?P<keep_or_discard>[+-])?(?P<discard_type>[LH])(?P<discard_count>\d+))?'
        r'(?:(?P<modifier_sign>[+-])(?P<modifier>\d+))?'
    )
    BIGGEST_DICE = 120
    ROLL_LIMIT = 100

    def __init__(self, rolls, sides, *,
                 discard_strategy: ResultsKeepStrategy = ResultsKeepStrategy.DEFAULT,
                 modifier=0):
        if not(0 < rolls <= self.ROLL_LIMIT):
            raise ValueRangeError('roll count', rolls, (1, self.ROLL_LIMIT))
        if not(0 < sides <= self.BIGGEST_DICE):
            raise ValueRangeError('sides', sides, (1, self.BIGGEST_DICE))
        self.rolls = rolls
        self.sides = sides
        self.modifier = modifier or 0
        self.discard_strategy = discard_strategy

    @staticmethod
    def parse(roll_str):
        match = Dice.__regex.fullmatch(roll_str)
        if not match:
            raise ParseError
        (
            rolls, sides,
            keep_or_discard, discard_type, discard_count,
            modifier_sign, modifier
        ) = match.groups()
        rolls = int(rolls) if rolls else 1
        sides = int(sides) if sides != '%' else 100
        discard_strategy = ResultsKeepStrategy.DEFAULT
        if discard_count:
            discard_count = min(rolls, int(discard_count))
            use_lowest = discard_type == 'L'
            keep = keep_or_discard is None or keep_or_discard == '+'
            discard_strategy = ResultsKeepStrategy(discard_count, keep=keep, lowest=use_lowest)
        modifier = int(modifier) if modifier else 0
        if modifier and modifier_sign == '-':
            modifier = -modifier
        return Dice(rolls, sides, discard_strategy=discard_strategy, modifier=modifier)

    def _single_roll(self):
        return random.randint(1, self.sides)

    def get_results(self, item_limit=None) -> Tuple[int, List[RollResult], bool]:
        if item_limit is None:
            return_count = self.rolls
        else:
            if item_limit < 0:
                raise ValueError('item limit should be non-negative!')
            return_count = min(self.rolls, item_limit)
        discarded_default = self.discard_strategy.get_discarded_default(self.rolls)
        results = [RollResult(self._single_roll(), is_discarded=discarded_default)
                   for _ in range(self.rolls)]
        return_results = results[:return_count]
        total = self.discard_strategy.apply(results) + self.modifier
        return total, return_results, return_count < self.rolls
