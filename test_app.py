import os
import unittest
from app import (
    init_db, add_book, add_member, search_book,
    issue_book, return_book, delete_book
)

TEST_DB = "test_library.db"

class TestLibrarySystem(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(TEST_DB)
        add_member("M101", "Rohan", "9876543210", "r@edu", TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_add_book(self):
        ok, _ = add_book(
            "B101", "Python Basics", "Guido", "Programming", 3, TEST_DB
        )
        self.assertTrue(ok)

    def test_search_book(self):
        add_book("B102", "DevOps Handbook", "Gene Kim", "DevOps", 2, TEST_DB)
        self.assertIsNotNone(search_book("B102", TEST_DB))

    def test_issue_and_return_book(self):
        add_book("B103", "Docker Deep Dive", "Nigel", "DevOps", 1, TEST_DB)
        self.assertTrue(issue_book("M101", "B103", TEST_DB)[0])
        self.assertFalse(issue_book("M101", "B103", TEST_DB)[0])
        self.assertTrue(return_book("M101", "B103", TEST_DB)[0])

    def test_delete_book(self):
        add_book("B104", "Git Pro", "Scott", "DevOps", 1, TEST_DB)
        ok, _ = delete_book("B104", TEST_DB)
        self.assertTrue(ok)

if __name__ == "__main__":
    unittest.main()