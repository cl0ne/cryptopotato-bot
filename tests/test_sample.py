import random
import unittest

from devpotato_bot.sample import sample_items_inplace


class ItemSamplerTest(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1024)

    def test_sample_items(self):
        item_count = 100
        for sample_size in range(item_count + 1):
            items = list(range(item_count))
            sample_items_inplace(items, sample_size)
            self.assertEqual(len(items), item_count)

            first_sampled_item = item_count - sample_size
            sample = set(items[first_sampled_item:])
            remainder = set(items[:first_sampled_item])

            self.assertEqual(len(sample), sample_size)
            self.assertEqual(len(sample) + len(remainder), item_count)
            self.assertTrue(remainder.isdisjoint(sample))

        empty = []
        with self.subTest(items=empty, sample_size=0):
            sample_items_inplace(empty, 0)
            self.assertEqual(len(empty), 0)

        self.assertRaises(ValueError, sample_items_inplace, empty, 1)
        self.assertRaises(ValueError, sample_items_inplace, [1], 2)
        self.assertRaises(ValueError, sample_items_inplace, empty, -1)

    def test_sample_items_limit(self):
        item_count = 60
        items = list(range(item_count))
        samples = []
        for sample_size, item_limit in ((10, None), (20, 50), (30, 30)):
            sample_items_inplace(items, sample_size, item_limit=item_limit)
            self.assertEqual(len(items), item_count)

            if item_limit is None:
                item_limit = item_count
            first_sampled_item = item_limit - sample_size
            sample = set(items[first_sampled_item:item_limit])
            remainder = set(items[:first_sampled_item])

            self.assertEqual(len(sample), sample_size)
            self.assertEqual(len(sample) + len(remainder), item_limit)
            for s in samples:
                with self.subTest(sample=sample, previous=s):
                    self.assertTrue(s.isdisjoint(sample))
            self.assertTrue(remainder.isdisjoint(sample))
            samples.append(sample)
        self.assertEqual(sum(len(s) for s in samples), item_count)

        empty = []
        with self.subTest(items=empty, sample_size=0, item_limit=0):
            sample_items_inplace(empty, 0, item_limit=0)
            self.assertEqual(len(empty), 0)

        for args in (
            dict(items=empty, sample_size=0, item_limit=1),
            dict(items=empty, sample_size=0, item_limit=-1),
            dict(items=empty, sample_size=1, item_limit=1),
            dict(items=[1], sample_size=1, item_limit=2),
            dict(items=[1], sample_size=2, item_limit=2)
        ):
            self.assertRaises(ValueError, sample_items_inplace, **args)


if __name__ == '__main__':
    unittest.main()
