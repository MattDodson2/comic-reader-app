import unittest

from issue_parser import expand_issue_range, extract_issues


class TestExpandIssueRange(unittest.TestCase):
    """
    Tests the conversion of issue numbers and ranges into lists.
    """

    def test_single_issue(self):

        # Expand a single issue number.
        result = expand_issue_range(10)

        # Check that the result contains only the specified issue.
        self.assertEqual(result, [10])


    def test_consecutive_issue_range(self):

        # Expand a consecutive range of issue numbers.
        result = expand_issue_range(1, 5)

        # Check that every issue in the range is included.
        self.assertEqual(result, [1, 2, 3, 4, 5])


    def test_invalid_issue_range(self):

        # Attempt to expand a range where the start exceeds the end.
        result = expand_issue_range(10, 5)

        # Check that an empty list is returned.
        self.assertEqual(result, [])


    def test_excessively_large_issue_range(self):

        # Attempt to expand a range exceeding the permitted size.
        result = expand_issue_range(1, 1500)

        # Check that the invalid range is rejected.
        self.assertEqual(result, [])


    def test_issue_zero(self):

        # Expand an issue numbered zero.
        result = expand_issue_range(0)

        # Check that issue zero is recognised.
        self.assertEqual(result, [0])


class TestExtractIssues(unittest.TestCase):
    """
    Tests the extraction of comic series and issue numbers
    from collected edition descriptions.
    """

    def test_single_series_with_range(self):

        # Create a description containing one comic series.
        description = "Collects Batman #404-407."

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected series and issue numbers.
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407]
            }
        ]

        # Check that the correct information was extracted.
        self.assertEqual(result, expected)


    def test_series_without_hash_symbol(self):

        # Create a description without hash symbols.
        description = (
            "Originally published in single magazine form as "
            "BATMAN: SHADOW OF THE BAT 1-12."
        )

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected series and issue numbers.
        expected = [
            {
                "series": "BATMAN: SHADOW OF THE BAT",
                "issues": list(range(1, 13))
            }
        ]

        # Check that the series and issue range were identified.
        self.assertEqual(result, expected)


    def test_multiple_comic_series(self):

        # Create a description containing two different series.
        description = (
            "Collects Batman #404-407, "
            "Detective Comics #575-578."
        )

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected results for both series.
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407]
            },
            {
                "series": "Detective Comics",
                "issues": [575, 576, 577, 578]
            }
        ]

        # Check that both series were identified correctly.
        self.assertEqual(result, expected)


    def test_additional_issues_from_same_series(self):

        # Create a description containing non-consecutive issues.
        description = "Collects Batman #404-407, #410, and #412."

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected issue numbers.
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407, 410, 412]
            }
        ]

        # Check that all issues belong to the same series.
        self.assertEqual(result, expected)


    def test_multiple_series_without_commas(self):

        # Create a description separating series using a conjunction.
        description = (
            "Collects Batman #404-407 "
            "and Detective Comics #575-578."
        )

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected results.
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407]
            },
            {
                "series": "Detective Comics",
                "issues": [575, 576, 577, 578]
            }
        ]

        # Check that both series were recognised.
        self.assertEqual(result, expected)


    def test_multiple_series_with_annual(self):

        # Create a description containing an annual issue.
        description = (
            "Collects Batman #404-407, "
            "Detective Comics #575-578, "
            "and Batman Annual #11."
        )

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected results.
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407]
            },
            {
                "series": "Detective Comics",
                "issues": [575, 576, 577, 578]
            },
            {
                "series": "Batman Annual",
                "issues": [11]
            }
        ]

        # Check that the annual is identified as a separate series.
        self.assertEqual(result, expected)


    def test_mixed_series_and_additional_issues(self):

        # Create a description containing several issue formats.
        description = (
            "Collects Batman #404-407, #410, and #412, "
            "Detective Comics #575-578 and Batman Annual #11."
        )

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected results.
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407, 410, 412]
            },
            {
                "series": "Detective Comics",
                "issues": [575, 576, 577, 578]
            },
            {
                "series": "Batman Annual",
                "issues": [11]
            }
        ]

        # Check that every issue belongs to the correct series.
        self.assertEqual(result, expected)


    def test_publication_year_in_series_title(self):

        # Create a description containing a publication year.
        description = "Collects Batman (1940) #404-407."

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected result without the publication year.
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407]
            }
        ]

        # Check that the publication year is not treated as an issue.
        self.assertEqual(result, expected)


    def test_duplicate_issue_numbers(self):

        # Create a description containing duplicate issue references.
        description = "Collects Batman #5, #3, #5, #1."

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected unique issue numbers.
        expected = [
            {
                "series": "Batman",
                "issues": [1, 3, 5]
            }
        ]

        # Check that duplicates are removed and issues are sorted.
        self.assertEqual(result, expected)


    def test_en_dash_issue_range(self):

        # Create a description using an en dash instead of a hyphen.
        description = "Collects Batman #5–7."

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected issue numbers.
        expected = [
            {
                "series": "Batman",
                "issues": [5, 6, 7]
            }
        ]

        # Check that the alternative range formatting is recognised.
        self.assertEqual(result, expected)


    def test_collecting_keyword(self):

        # Create a description beginning with 'Collecting'.
        description = "Collecting Batman #1-3."

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected results.
        expected = [
            {
                "series": "Batman",
                "issues": [1, 2, 3]
            }
        ]

        # Check that the alternative introductory phrase is recognised.
        self.assertEqual(result, expected)


    def test_description_without_collection_information(self):

        # Create a description without a recognised collection phrase.
        description = "Batman #404-407 tells the story of Bruce Wayne."

        # Attempt to extract collected issues.
        result = extract_issues(description)

        # Check that no issues are returned.
        self.assertEqual(result, [])


    def test_empty_description(self):

        # Attempt to extract issues from an empty description.
        result = extract_issues("")

        # Check that an empty list is returned.
        self.assertEqual(result, [])


if __name__ == "__main__":

    # Run all tests in this file.
    unittest.main()