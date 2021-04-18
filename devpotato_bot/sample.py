import random
from typing import TypeVar, MutableSequence

T = TypeVar('T')


def sample_items_inplace(items: MutableSequence[T], sample_size: int, item_limit: int = None):
    """Moves sampled elements to the end of items list.

    When the sample size is equal to the size of the items list, it merely shuffles items in-place.
    """
    n = len(items)
    if item_limit is None:
        item_limit = n
    elif not 0 <= item_limit <= n:
        raise ValueError("Item limit is negative or larger than item list size")
    if not 0 <= sample_size <= n:
        raise ValueError("Sample size is negative or larger than items list")
    if sample_size > item_limit:
        raise ValueError("Sample size is greater than item limit")
    for i in range(sample_size):
        j = random.randrange(item_limit - i)
        current_index = item_limit - i - 1
        if current_index != j:
            tmp = items[j]
            items[j] = items[current_index]
            items[current_index] = tmp
