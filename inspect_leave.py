import unittest

def add(x, y):
    return x + y

class TestAdd(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(1, 2), 3)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -2), -3)

    def test_add_mixed_numbers(self):
        self.assertEqual(add(1, -2), -1)

    def test_add_zero(self):
        self.assertEqual(add(0, 5), 5)

if __name__ == '__main__':
    unittest.main()