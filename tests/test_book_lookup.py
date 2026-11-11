
import os
import unittest

from unittest.mock import patch

from book_lookup import get_book_info
from penguin_random_house import find_flap_copy, clean_description
from penguin_random_house import find_title_record


class TestBookLookup(unittest.TestCase):
    """
    Tests the selection of book metadata providers.
    """

    def setUp(self):

        # Configures a temporary PRH API key
        key_patch = patch.dict(
            os.environ,
            {"PRH_API_KEY": "test-key"}
        )

        # Activates the temporary environment variable
        key_patch.start()

        # Restores the original environment after each test
        self.addCleanup(key_patch.stop)


    @patch("book_lookup.get_google_book_info")
    @patch("book_lookup.get_prh_book_info")
    def test_prh_is_primary(self, mock_prh, mock_google):

        # Simulates a complete PRH book record
        mock_prh.return_value = {
            "title": "Robin: Tim Drake Compendium Book One",
            "subtitle": "",
            "publisher": "DC Comics",
            "description": "Collects Robin #1-5.",
            "source": "Penguin Random House"
        }

        # Retrieves the book information
        result = get_book_info("9781779525932")

        # Checks that PRH supplied the result
        self.assertEqual(
            result["source"],
            "Penguin Random House"
        )

        # Checks that Google Books was not contacted
        mock_google.assert_not_called()


    @patch("book_lookup.get_google_book_info")
    @patch("book_lookup.get_prh_book_info")
    def test_google_books_fallback(self, mock_prh, mock_google):

        # Simulates PRH returning no matching book
        mock_prh.return_value = None

        # Simulates Google Books identifying the book
        mock_google.return_value = {
            "title": "Batman",
            "subtitle": "",
            "publisher": "DC Comics",
            "description": "Collects Batman #1-5."
        }

        # Retrieves the book information
        result = get_book_info("9781401263195")

        # Checks that Google Books supplied the result
        self.assertEqual(
            result["source"],
            "Google Books (fallback)"
        )


    @patch("book_lookup.get_google_book_info")
    @patch("book_lookup.get_prh_book_info")
    def test_missing_prh_description(self, mock_prh, mock_google):

        # Simulates an incomplete PRH record
        mock_prh.return_value = {
            "title": "Batman",
            "subtitle": "",
            "publisher": "DC Comics",
            "description": "",
            "source": "Penguin Random House"
        }

        # Simulates a more complete Google Books record
        mock_google.return_value = {
            "title": "Batman",
            "subtitle": "",
            "publisher": "DC Comics",
            "description": "Collects Batman #1-5."
        }

        # Retrieves the book information
        result = get_book_info("9781401263195")

        # Checks that the fallback description was used
        self.assertEqual(
            result["description"],
            "Collects Batman #1-5."
        )


    @patch("book_lookup.get_google_book_info")
    @patch("book_lookup.get_prh_book_info")
    def test_book_not_found(self, mock_prh, mock_google):

        # Simulates both databases returning no book
        mock_prh.return_value = None
        mock_google.return_value = None

        # Attempts to retrieve the book
        result = get_book_info("0000000000000")

        # Checks that no book was returned
        self.assertIsNone(result)


    def test_flap_copy_extraction(self):

        # Creates a simulated nested PRH content response
        data = {
            "data": {
                "content": {
                    "flap_copy": "<p>Collects Robin #1-5.</p>"
                }
            }
        }

        # Extracts and clean the description
        description = clean_description(find_flap_copy(data))

        # Checks that the correct description was retrieved
        self.assertEqual(description, "Collects Robin #1-5.")

    
    def test_nested_prh_title_metadata(self):

        # Creates a simulated PRH response with nested metadata
        data = {
            "status": "ok",
            "data": {
                "titles": [
                    {
                        "isbn": 9781779525932,
                        "title": "Robin: Tim Drake Compendium Book One",
                        "consumerImprint": "DC Comics"
                    }
                ]
            }
        }

        # Searches for the requested book record
        result = find_title_record(data, "9781779525932")

        # Checks that the title was identified correctly
        self.assertEqual(
            result["title"],
            "Robin: Tim Drake Compendium Book One"
        )

        # Checks that the publisher information was found
        self.assertEqual(result["consumerImprint"], "DC Comics")

if __name__ == "__main__":

    # Runs the unit tests
    unittest.main()
