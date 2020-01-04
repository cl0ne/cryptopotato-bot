import random
import re
from typing import List, Tuple


class Dice:
    __r = re.compile(
        r'(?P<rolls>[1-9]\d*)?'
        r'd'
        r'(?P<sides>[1-9]\d*)'
    )
    
    def __init__(self, rolls, sides):
        self.rolls = rolls
        self.sides = sides
    
    @staticmethod
    def parse(roll_str):
        match = Dice.__r.fullmatch(roll_str)
        if not match:
            raise ValueError('Roll is not in dice notation')
        rolls, sides = match.groups()
        rolls = int(rolls) if rolls else 1
        sides = int(sides)
        return Dice(rolls, sides)

    def _single_roll(self):
        return random.randint(1, self.sides)

    def get_result(self, item_limit=None) -> Tuple[int, List[int], bool]:
        total = 0
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
            total += sum(self._single_roll() for i in range(item_limit, self.rolls))
        return total, items, item_count < self.rolls
