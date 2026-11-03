import os
import unittest
import requests

from unittest.mock import Mock, call, patch

from isbn_lookup import get_book_info, display_book_info, main


def create_mock_response(status_code, data=None):
    """
    Creates a simulated HTTP response for testing.
    """

    # Create a mock response object.
    response = Mock()

    # Assign the HTTP status code.
    response.status_code = status_code

    # Configure the JSON data returned by the response.
    response.json.return_value = data if data is not None else {}

    # Return the configured response.
    return response


class TestGetBookInfo(unittest.TestCase):
    """
    Tests retrieving book information from the Google Books API.
    """

    def setUp(self):
        """
        Configures a temporary API key for each test.
        """

        # Replace the real API key with a dummy value.
        self.api_key_patch = patch.dict(
            os.environ,
            {"GOOGLE_BOOKS_API_KEY": "test-api-key"}
        )

        # Activate the temporary environment variable.
        self.api_key_patch.start()

        # Restore the original environment when the test finishes.
        self.addCleanup(self.api_key_patch.stop)


    @patch("isbn_lookup.requests.get")
    def test_successful_book_lookup(self, mock_get):

        # Create a simulated Google Books response.
        data = {
            "items": [
                {
                    "volumeInfo": {
                        "title": "Batman: Shadow of the Bat",
                        "subtitle": "Volume 1",
                        "publisher": "DC Comics",
                        "description": "Collects Batman #1-12."
                    }
                }
            ]
        }

        # Configure the API request to return a successful response.
        mock_get.return_value = create_mock_response(200, data)

        # Retrieve the simulated book information.
        result = get_book_info("9781401263195")

        # Check that the correct title was returned.
        self.assertEqual(result["title"], "Batman: Shadow of the Bat")

        # Check that the correct subtitle was returned.
        self.assertEqual(result["subtitle"], "Volume 1")

        # Check that the correct publisher was returned.
        self.assertEqual(result["publisher"], "DC Comics")

        # Check that the description was retrieved.
        self.assertEqual(result["description"], "Collects Batman #1-12.")

        # Retrieve the arguments supplied to the simulated API request.
        request_arguments = mock_get.call_args.kwargs

        # Check that the correct ISBN was submitted.
        self.assertEqual(
            request_arguments["params"]["q"],
            "isbn:9781401263195"
        )

        # Check that the API key was included.
        self.assertEqual(
            request_arguments["params"]["key"],
            "test-api-key"
        )


    @patch("isbn_lookup.requests.get")
    def test_book_not_found(self, mock_get):

        # Simulate a successful response containing no books.
        mock_get.return_value = create_mock_response(
            200,
            {"items": []}
        )

        # Attempt to retrieve an unknown book.
        result = get_book_info("0000000000000")

        # Check that None is returned.
        self.assertIsNone(result)


    @patch("isbn_lookup.requests.get")
    def test_missing_book_information(self, mock_get):

        # Simulate a record containing only a book title.
        data = {
            "items": [
                {
                    "volumeInfo": {
                        "title": "BATMAN"
                    }
                }
            ]
        }

        # Configure the simulated response.
        mock_get.return_value = create_mock_response(200, data)

        # Retrieve the incomplete book record.
        result = get_book_info("9781779528353")

        # Check that the available title is preserved.
        self.assertEqual(result["title"], "BATMAN")

        # Check that missing publisher information is handled.
        self.assertEqual(result["publisher"], "Unknown")

        # Check that a missing description produces an empty string.
        self.assertEqual(result["description"], "")

        # Check that a missing subtitle produces an empty string.
        self.assertEqual(result["subtitle"], "")


    @patch("isbn_lookup.time.sleep")
    @patch("isbn_lookup.requests.get")
    def test_retry_after_server_error(self, mock_get, mock_sleep):

        # Create a simulated temporary server error.
        failed_response = create_mock_response(503)

        # Create a successful response containing book information.
        successful_response = create_mock_response(
            200,
            {
                "items": [
                    {
                        "volumeInfo": {
                            "title": "Batman",
                            "description": "Collects Batman #1-5."
                        }
                    }
                ]
            }
        )

        # Return the failed response followed by the successful response.
        mock_get.side_effect = [
            failed_response,
            successful_response
        ]

        # Attempt to retrieve the book.
        result = get_book_info("9781401263195")

        # Check that the book was eventually retrieved.
        self.assertEqual(result["title"], "Batman")

        # Check that two API requests were made.
        self.assertEqual(mock_get.call_count, 2)

        # Check that the application waited before retrying.
        mock_sleep.assert_called_once_with(1)


    @patch("isbn_lookup.time.sleep")
    @patch("isbn_lookup.requests.get")
    def test_maximum_retry_attempts(self, mock_get, mock_sleep):

        # Simulate repeated temporary server errors.
        mock_get.return_value = create_mock_response(503)

        # Check that a RuntimeError is raised after all attempts fail.
        with self.assertRaisesRegex(RuntimeError, "HTTP 503"):

            # Attempt to retrieve the book.
            get_book_info("9781401263195")

        # Check that no more than three requests were made.
        self.assertEqual(mock_get.call_count, 3)

        # Check that the delays increase between attempts.
        self.assertEqual(
            mock_sleep.call_args_list,
            [call(1), call(2)]
        )


    @patch("isbn_lookup.time.sleep")
    @patch("isbn_lookup.requests.get")
    def test_non_retryable_api_error(self, mock_get, mock_sleep):

        # Simulate an API quota error.
        mock_get.return_value = create_mock_response(429)

        # Check that the unsuccessful response raises an error.
        with self.assertRaisesRegex(RuntimeError, "HTTP 429"):

            # Attempt to retrieve the book.
            get_book_info("9781401263195")

        # Check that the application did not retry the request.
        mock_get.assert_called_once()

        # Check that no retry delay was introduced.
        mock_sleep.assert_not_called()


    @patch("isbn_lookup.requests.get")
    def test_network_connection_error(self, mock_get):

        # Simulate a network connection failure.
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        # Check that the connection error is propagated.
        with self.assertRaises(requests.exceptions.ConnectionError):

            # Attempt to retrieve the book.
            get_book_info("9781401263195")


class TestDisplayBookInfo(unittest.TestCase):
    """
    Tests displaying book information and collected issues.
    """

    def setUp(self):
        """
        Creates a sample book record for each test.
        """

        # Store a reusable book record.
        self.book = {
            "title": "Batman",
            "subtitle": "Volume 1",
            "publisher": "DC Comics",
            "description": "Collects Batman #1-5."
        }


    @patch("builtins.print")
    @patch("isbn_lookup.extract_issues")
    def test_successful_issue_display(self, mock_extract, mock_print):

        # Simulate a successful issue extraction.
        mock_extract.return_value = [
            {
                "series": "Batman",
                "issues": [1, 2, 3, 4, 5]
            }
        ]

        # Display the book information.
        result = display_book_info(self.book)

        # Check that the operation succeeded.
        self.assertTrue(result)

        # Check that the series title was displayed.
        mock_print.assert_any_call("\nBatman")

        # Check that the final issue was displayed.
        mock_print.assert_any_call("  #5")


    @patch("builtins.print")
    @patch("isbn_lookup.extract_issues")
    def test_missing_description(self, mock_extract, mock_print):

        # Remove the description from the sample book.
        self.book["description"] = ""

        # Attempt to display the book information.
        result = display_book_info(self.book)

        # Check that the operation was unsuccessful.
        self.assertFalse(result)

        # Check that issue extraction was not attempted.
        mock_extract.assert_not_called()

        # Check that an appropriate message was displayed.
        mock_print.assert_any_call(
            "\nNo description is available for this book."
        )


    @patch("builtins.print")
    @patch("isbn_lookup.extract_issues")
    def test_description_without_recognised_issues(
        self,
        mock_extract,
        mock_print
    ):

        # Replace the description with one containing no issue information.
        self.book["description"] = "A story about Batman."

        # Simulate the parser finding no collected issues.
        mock_extract.return_value = []

        # Attempt to display the book information.
        result = display_book_info(self.book)

        # Check that the operation was unsuccessful.
        self.assertFalse(result)

        # Check that the correct description was passed to the parser.
        mock_extract.assert_called_once_with(
            "A story about Batman."
        )

        # Check that the missing issue information was reported.
        mock_print.assert_any_call(
            "\nUnable to identify collected issues from the description."
        )


class TestMain(unittest.TestCase):
    """
    Tests the application's user interaction.
    """

    @patch("builtins.print")
    @patch(
        "builtins.input",
        side_effect=["0000000000000", "9781401263195", "q"]
    )
    @patch("isbn_lookup.get_book_info")
    @patch("isbn_lookup.display_book_info")
    def test_multiple_isbn_searches(
        self,
        mock_display,
        mock_lookup,
        mock_input,
        mock_print
    ):

        # Create a sample book record.
        book = {
            "title": "Batman",
            "subtitle": "",
            "publisher": "DC Comics",
            "description": "Collects Batman #1-5."
        }

        # Simulate a failed lookup followed by a successful lookup.
        mock_lookup.side_effect = [None, book]

        # Simulate successful processing of the second book.
        mock_display.return_value = True

        # Run the application's main loop.
        main()

        # Check that both ISBNs were searched.
        self.assertEqual(
            mock_lookup.call_args_list,
            [
                call("0000000000000"),
                call("9781401263195")
            ]
        )

        # Check that the successful book was displayed.
        mock_display.assert_called_once_with(book)

        # Check that the application accepted three user inputs.
        self.assertEqual(mock_input.call_count, 3)


if __name__ == "__main__":

    # Run all tests in this file.
    unittest.main()