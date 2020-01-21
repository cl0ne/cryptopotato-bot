import random
import re
from typing import List, Tuple, Optional


class ParseError(Exception):
    def __init__(self):
        super().__init__('Roll is not in dice notation')


class ValueRangeError(ValueError):
    def __init__(self, arg_name, value,
                 allowed_range: Optional[Tuple[Optional[int], Optional[int]]] = None):
        self.arg_name = arg_name
        self.value = value
        self.allowed_range = allowed_range
        super().__init__({
            'arg_name': arg_name,
            'value': value,
            'allowed_range': allowed_range
        })
    
    @property
    def message(self):
        if self.allowed_range is None or self.allowed_range == (None, None):
            return '{arg_name} has unacceptable value: {value}'
        arg_min, arg_max = self.allowed_range
        if arg_max is None:
            return '{arg_name} is less than {allowed_range[0]}: {value}'
        if arg_min is None:
            return '{arg_name} is greater than {allowed_range[1]}: {value}'
        return '{arg_name} is not between {allowed_range[0]} and {allowed_range[1]}: {value}'
    
    @property
    def formatted_message(self):
        return self.message.format(**self.args[0])


class Dice:
    __regex = re.compile(
        r'(?P<rolls>\d+)?'
        r'd'
        r'(?P<sides>\d+|%)'
        r'(?:(?P<modifier_sign>[+-])(?P<modifier>\d+))?'
    )
    BIGGEST_DICE = 120
    ROLL_LIMIT = 100

    def __init__(self, rolls, sides, modifier=0):
        if not(0 < rolls <= self.ROLL_LIMIT):
            raise ValueRangeError('roll count', rolls, (1, self.ROLL_LIMIT))
        if not(0 < sides <= self.BIGGEST_DICE):
            raise ValueRangeError('sides', sides, (1, self.BIGGEST_DICE))
        self.rolls = rolls
        self.sides = sides
        self.modifier = modifier or 0

    @staticmethod
    def parse(roll_str):
        match = Dice.__regex.fullmatch(roll_str)
        if not match:
            raise ParseError
        rolls, sides, modifier_sign, modifier = match.groups()
        rolls = int(rolls) if rolls else 1
        sides = int(sides) if sides != '%' else 100
        modifier = int(modifier) if modifier else 0
        if modifier and modifier_sign == '-':
            modifier = -modifier
        return Dice(rolls, sides, modifier)

    def _single_roll(self):
        return random.randint(1, self.sides)

    def get_result(self, item_limit=None) -> Tuple[int, List[int], bool]:
        total = self.modifier
        items = []
        if item_limit is None:
            item_count = self.rolls
        else:
            item_count = min(self.rolls, item_limit)
            if item_limit < 0:
                raise ValueError('item limit should be non-negative!')
        for i in range(item_count):
            r = self._single_roll()
            total += r
            items.append(r)
        if item_limit is not None:
            total += sum(self._single_roll() for _ in range(item_limit, self.rolls))
        return total, items, item_count < self.rolls
