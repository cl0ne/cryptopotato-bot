import operator
import random


def partition(items, left, right, pivot_index, compare):
    """Groups items between left and right index into two parts:
    those less than element at pivot_index, and those greater than or equal to it
    """
    assert 0 <= left <= pivot_index <= right < len(items)
    if left == right:
        return pivot_index

    pivot_value = items[pivot_index]
    items[right], items[pivot_index] = items[pivot_index], items[right]
    pivot_index = left
    for i in range(left, right):
        if compare(items[i], pivot_value):
            items[pivot_index], items[i] = items[i], items[pivot_index]
            pivot_index += 1
    items[right], items[pivot_index] = items[pivot_index], items[right]
    return pivot_index


def select(items, k, compare=operator.lt):
    """Reorders items in-place so that first k items are the lowest (largest) ones

    A custom compare function can be supplied to customize comparison of the items.
    The function uses quickselect algorithm with minor modifications."""
    if not items or k == 0 or k == len(items):
        return
    if k < 0:
        raise ValueError('k should not be less than zero')
    if k > len(items):
        raise ValueError('k should not be greater than item count')
    left = 0
    right = len(items) - 1
    while True:
        if left == right:
            break
        pivot_index = random.randint(left, right)
        pivot_index = partition(items, left, right, pivot_index, compare)
        if (k - 1) == pivot_index:
            break
        elif (k - 1) < pivot_index:
            right = pivot_index - 1
        else:
            left = pivot_index + 1
