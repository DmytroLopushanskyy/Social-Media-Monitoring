"""
Unittest for is_sorted module
"""
from classes.keyword import Keywords
from unittest import TestCase

dict

class TestIsSorted(TestCase):
    """
    Test is_sorted function
    """
    def setUp(self):
        """
        Initialize several class instances.
        """
        keywords = Keywords()


    def test_main_cases(self):
        """
        Test main cases
        """
        lst = [34, 87, 12, 45, 78]
        self.assertEqual(False, is_sorted(lst))

        lst = [12, 34, 67, 98]
        self.assertEqual(True, is_sorted(lst))

    def test_empty_list(self):
        """
        Test an empty list case
        """
        lst = []
        self.assertEqual(True, is_sorted(lst))

    def test_negative_values(self):
        """
        Test negative values case
        """
        lst = [-45, -30, 0]
        self.assertEqual(True, is_sorted(lst))

        lst = [-45, -60, -20, -80, -100, 56]
        self.assertEqual(False, is_sorted(lst))

    def test_equal_elements(self):
        """
        Test equal elements case
        """
        lst = [25, 25, 25, 25]
        self.assertEqual(True, is_sorted(lst))

    def test_wrong_data_input(self):
        """
        Test when wrong data is entered
        """
        lst = [-45, -60, "", -80, -100, 56]
        self.assertRaises(WrongInput, is_sorted, lst)

        lst = [-45, -100, True]
        self.assertRaises(WrongInput, is_sorted, lst)

        lst = [-45, -100, (100, )]
        self.assertRaises(WrongInput, is_sorted, lst)

        lst = "Not list input"
        self.assertRaises(WrongInput, is_sorted, lst)

    def test_big_input(self):
        """
        Test big data input case
        """
        lst = random.sample(range(100000), 10)
        if lst != lst.copy().sort():
            self.assertEqual(False, is_sorted(lst))
        else:
            self.assertEqual(True, is_sorted(lst))
