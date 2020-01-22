import itertools
import random
import unittest

from devpotato_bot.quickselect import partition, select


class ItemSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ordered = tuple(range(1, 11))
        shuffled = list(ordered)
        random.seed(1024)
        random.shuffle(shuffled)
        random_items = tuple(random.randint(1, 10) for _ in range(10))
        cls.items_pool = (
            ('reversed', tuple(reversed(ordered)), ordered),
            ('shuffled', tuple(shuffled), ordered),
            ('random', random_items, tuple(sorted(random_items)))
        )

    def setUp(self) -> None:
        random.seed(1024)

    def test_select_noop(self):
        for n in [0, 1, 10]:
            original_items = list(range(n))
            items = list(original_items)
            select(items, 0)
            self.assertEqual(original_items, items)

            items = list(original_items)
            select(items, n)
            self.assertEqual(original_items, items)

        self.assertRaises(ValueError, select, list([1, 2]), -1)
        self.assertRaises(ValueError, select, list([1, 2]), 3)

    def test_select_sorted(self):
        items = list(range(10))
        select(items, 4)
        self.assertSequenceEqual(range(10), items)

        items = list(range(10)[::-1])
        select(items, 4, compare=int.__gt__)
        self.assertSequenceEqual(range(10)[::-1], items)

    def test_select(self):
        for item_set_name, items, ordered in self.items_pool:
            for k in range(1, len(items)):
                with self.subTest(item_set=item_set_name, k=k):
                    selected = list(items)
                    select(selected, k)
                    self.assertEqual(ordered[k-1], selected[k-1])
                    self.assertSequenceEqual(ordered, sorted(selected[:k]) + sorted(selected[k:]))

    @staticmethod
    def get_pivot_combinations(items):
        n = len(items)
        for left in range(n - 1):
            for right in range(left, n):
                for pivot_i in range(left, right + 1):
                    yield left, right, pivot_i

    def test_partition(self):
        for item_set_name, original_items, _ in self.items_pool:
            for left, right, pivot_i in self.get_pivot_combinations(original_items):
                with self.subTest(item_set=item_set_name, left=left, right=right, pivot_i=pivot_i):
                    items = list(original_items)
                    new_pivot_i = partition(items, left, right, pivot_i, int.__lt__)

                    # check ordering within [left; right]
                    pivot = original_items[pivot_i]
                    self.assertEqual(pivot, items[new_pivot_i])
                    self.assertTrue(all(x < pivot for x in items[left:new_pivot_i]))
                    self.assertTrue(all(x >= pivot for x in items[new_pivot_i+1:right+1]))

                    # order of items outside of [left; right] range is unchanged
                    self.assertSequenceEqual(items[:left], original_items[:left])
                    self.assertSequenceEqual(items[right+1:], original_items[right+1:])


if __name__ == '__main__':
    unittest.main()
