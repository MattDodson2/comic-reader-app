import unittest

from issue_parser import expand_issue_range, extract_issues


class TestExpandIssueRange(unittest.TestCase):
    """
    Tests the conversion of issue numbers and ranges into lists.
    """

    def test_single_issue(self):

        # Expand a single issue number
        result = expand_issue_range(10)

        # Check that the result contains only the specified issue
        self.assertEqual(result, [10])


    def test_consecutive_issue_range(self):

        # Expand a consecutive range of issue numbers
        result = expand_issue_range(1, 5)

        # Check that every issue in the range is included
        self.assertEqual(result, [1, 2, 3, 4, 5])


    def test_invalid_issue_range(self):

        # Attempt to expand a range where the start exceeds the end
        result = expand_issue_range(10, 5)

        # Check that an empty list is returned
        self.assertEqual(result, [])


    def test_excessively_large_issue_range(self):

        # Attempt to expand a range exceeding the permitted size
        result = expand_issue_range(1, 1500)

        # Check that the invalid range is rejected
        self.assertEqual(result, [])


    def test_issue_zero(self):

        # Expand an issue numbered zero
        result = expand_issue_range(0)

        # Check that issue zero is recognised
        self.assertEqual(result, [0])


class TestExtractIssues(unittest.TestCase):
    """
    Tests the extraction of comic series and issue numbers
    from collected edition descriptions.
    """

    def test_single_series_with_range(self):

        # Create a description containing one comic series
        description = "Collects Batman #404-407."

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected series and issue numbers
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407]
            }
        ]

        # Check that the correct information was extracted
        self.assertEqual(result, expected)


    def test_series_without_hash_symbol(self):

        # Create a description without hash symbols
        description = (
            "Originally published in single magazine form as "
            "BATMAN: SHADOW OF THE BAT 1-12."
        )

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected series and issue numbers
        expected = [
            {
                "series": "BATMAN: SHADOW OF THE BAT",
                "issues": list(range(1, 13))
            }
        ]

        # Check that the series and issue range were identified
        self.assertEqual(result, expected)


    def test_multiple_comic_series(self):

        # Create a description containing two different series
        description = (
            "Collects Batman #404-407, "
            "Detective Comics #575-578."
        )

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected results for both series
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

        # Check that both series were identified correctly
        self.assertEqual(result, expected)


    def test_additional_issues_from_same_series(self):

        # Create a description containing non-consecutive issues
        description = "Collects Batman #404-407, #410, and #412."

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected issue numbers
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407, 410, 412]
            }
        ]

        # Check that all issues belong to the same series
        self.assertEqual(result, expected)


    def test_multiple_series_without_commas(self):

        # Create a description separating series using a conjunction
        description = (
            "Collects Batman #404-407 "
            "and Detective Comics #575-578."
        )

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected results
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

        # Check that both series were recognised
        self.assertEqual(result, expected)


    def test_multiple_series_with_annual(self):

        # Create a description containing an annual issue
        description = (
            "Collects Batman #404-407, "
            "Detective Comics #575-578, "
            "and Batman Annual #11."
        )

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected results
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

        # Check that the annual is identified as a separate series
        self.assertEqual(result, expected)


    def test_mixed_series_and_additional_issues(self):

        # Create a description containing several issue formats
        description = (
            "Collects Batman #404-407, #410, and #412, "
            "Detective Comics #575-578 and Batman Annual #11."
        )

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected results
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

        # Check that every issue belongs to the correct series
        self.assertEqual(result, expected)


    def test_publication_year_in_series_title(self):

        # Create a description containing a publication year
        description = "Collects Batman (1940) #404-407."

        # Extract the collected issues.
        result = extract_issues(description)

        # Define the expected result without the publication year
        expected = [
            {
                "series": "Batman",
                "issues": [404, 405, 406, 407]
            }
        ]

        # Check that the publication year is not treated as an issue
        self.assertEqual(result, expected)


    def test_duplicate_issue_numbers(self):

        # Create a description containing duplicate issue references
        description = "Collects Batman #5, #3, #5, #1."

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected unique issue numbers
        expected = [
            {
                "series": "Batman",
                "issues": [1, 3, 5]
            }
        ]

        # Check that duplicates are removed and issues are sorted
        self.assertEqual(result, expected)


    def test_en_dash_issue_range(self):

        # Create a description using an en dash instead of a hyphen
        description = "Collects Batman #5–7."

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected issue numbers
        expected = [
            {
                "series": "Batman",
                "issues": [5, 6, 7]
            }
        ]

        # Check that the alternative range formatting is recognised
        self.assertEqual(result, expected)


    def test_collecting_keyword(self):

        # Create a description beginning with 'Collecting'
        description = "Collecting Batman #1-3."

        # Extract the collected issues
        result = extract_issues(description)

        # Define the expected results
        expected = [
            {
                "series": "Batman",
                "issues": [1, 2, 3]
            }
        ]

        # Check that the alternative introductory phrase is recognised
        self.assertEqual(result, expected)


    def test_description_without_collection_information(self):

        # Create a description without a recognised collection phrase
        description = "Batman #404-407 tells the story of Bruce Wayne."

        # Attempt to extract collected issues
        result = extract_issues(description)

        # Check that no issues are returned
        self.assertEqual(result, [])


    def test_empty_description(self):

        # Attempt to extract issues from an empty description
        result = extract_issues("")

        # Check that an empty list is returned
        self.assertEqual(result, [])

    
    def test_tim_drake_compendium_description(self):

        # Creates the collection statement from the PRH description
        description = (
            "Collects Batman #455-457, #465-469, #480, "
            "Detective Comics #618-621, "
            "Robin (vol. 1) #1-5, "
            "Robin II: The Joker’s Wild! #1-4, "
            "Robin III: Cry of the Huntress #1-6, "
            "Robin (vol. 2) #1-5, "
            "Robin Annual #1-2, "
            "Superman (vol. 2) #70, "
            "Superman: The Man of Steel #14, "
            "and stories from Batman 80-Page Giant #2 "
            "and Showcase ’93 #1-6, #11-12."
        )

        # Extracts the collected issues
        results = extract_issues(description)

        # Checks that all eleven series were identified
        self.assertEqual(len(results), 11)

        # Checks the two separate Robin volumes
        self.assertEqual(results[2]["series"], "Robin (vol. 1)")
        self.assertEqual(results[5]["series"], "Robin (vol. 2)")

        # Checks the second volume's issue numbers
        self.assertEqual(results[5]["issues"], [1, 2, 3, 4, 5])

        # Checks the issues collected from Showcase '93
        self.assertEqual(
            results[10]["issues"],
            [1, 2, 3, 4, 5, 6, 11, 12]
        )

        # Checks that the final series contains selected stories
        self.assertTrue(results[10]["partial"])


    def test_volume_abbreviation_does_not_end_description(self):

        # Creates a description containing a volume abbreviation
        description = (
            "Collects Robin (vol. 1) #1-5 "
            "and Robin Annual #1-2."
        )

        # Extracts the collected issues
        results = extract_issues(description)

        # Checks that both series were identified
        self.assertEqual(len(results), 2)

        # Checks that the annual is included
        self.assertEqual(results[1]["series"], "Robin Annual")
        self.assertEqual(results[1]["issues"], [1, 2])

    
    def test_batgirl_prh_description(self):

        # Creates the collection statement from PRH
        description = (
            "This volume colles issues 1-6 of Batgirl, "
            "part of the DC Comics—The New 52 event."
        )

        # Extracts the collected issues
        result = extract_issues(description)

        # Defines the expected series and issues
        expected = [{
            "series": "Batgirl",
            "issues": [1, 2, 3, 4, 5, 6]
        }]

        # Checks that the correct issues are identified
        self.assertEqual(result, expected)

    def test_issues_before_series_title(self):

        # Creates a description using the standard wording
        description = (
            "This volume collects issues #1-6 of Batgirl."
        )

        # Extracts the collected issues
        result = extract_issues(description)

        # Defines the expected result
        expected = [{
            "series": "Batgirl",
            "issues": [1, 2, 3, 4, 5, 6]
        }]

        # Checks that the alternative format is recognised
        self.assertEqual(result, expected)


    def test_bruce_wayne_murderer(self):

        # Creates a description containing semicolon-separated series
        description = (
            "This edition collects Batgirl 24, 27; "
            "Batman 599-602; "
            "Batman: Gotham Knights 25-28; "
            "Batman: the 10-cent adventure 1; "
            "Birds of prey 39, 40-41, 43; "
            "Detective comics 766-767; "
            "Nightwing 65-66, 68-69; "
            "Robin 98-99."
        )

        # Extracts the collected issues
        results = extract_issues(description)

        # Defines the expected comic series and issues
        expected = [
            {"series": "Batgirl", "issues": [24, 27]},
            {"series": "Batman", "issues": [599, 600, 601, 602]},
            {"series": "Batman: Gotham Knights", "issues": [25, 26, 27, 28]},
            {"series": "Batman: the 10-cent adventure", "issues": [1]},
            {"series": "Birds of prey", "issues": [39, 40, 41, 43]},
            {"series": "Detective comics", "issues": [766, 767]},
            {"series": "Nightwing", "issues": [65, 66, 68, 69]},
            {"series": "Robin", "issues": [98, 99]}
        ]

        # Checks that every series and issue number is correct
        self.assertEqual(results, expected)

    
    def test_unprefixed_issues_with_semicolons(self):

        # Creates a description with semicolon-separated series
        description = (
            "Collects Batgirl 24, 27; Batman 599-602; "
            "Batman: Gotham Knights 25-28; "
            "Batman: The 10-Cent Adventure 1; "
            "Birds of Prey 39, 40-41, 43; "
            "Detective Comics 766-767; "
            "Nightwing 65-66, 68-69; Robin 98-99."
        )

        # Extracts the collected issues
        results = extract_issues(description)

        # Defines the expected series and issues
        expected = [
            {"series": "Batgirl", "issues": [24, 27]},
            {"series": "Batman", "issues": [599, 600, 601, 602]},
            {"series": "Batman: Gotham Knights", "issues": [25, 26, 27, 28]},
            {"series": "Batman: The 10-Cent Adventure", "issues": [1]},
            {"series": "Birds of Prey", "issues": [39, 40, 41, 43]},
            {"series": "Detective Comics", "issues": [766, 767]},
            {"series": "Nightwing", "issues": [65, 66, 68, 69]},
            {"series": "Robin", "issues": [98, 99]}
        ]

        # Checks that every series and issue is correct
        self.assertEqual(results, expected)


    def test_unprefixed_issues_with_commas(self):

        # Creates a description with comma-separated series
        description = (
            "Collects Batgirl 24, 27, Batman 599-602, "
            "Batman: Gotham Knights 25-28, "
            "Batman: The 10-Cent Adventure 1, "
            "Birds of Prey 39, 40-41, 43, "
            "Detective Comics 766-767, "
            "Nightwing 65-66, 68-69 and Robin 98-99."
        )

        # Extracts the collected issues
        results = extract_issues(description)

        # Checks that all eight series are recognised
        self.assertEqual(len(results), 8)

        # Checks that the Batgirl issues are separated correctly
        self.assertEqual(results[0]["series"], "Batgirl")
        self.assertEqual(results[0]["issues"], [24, 27])

        # Checks that the Batman issues are separated correctly
        self.assertEqual(results[1]["series"], "Batman")
        self.assertEqual(results[1]["issues"], [599, 600, 601, 602])

        # Checks that the final Robin issues are correct
        self.assertEqual(results[7]["series"], "Robin")
        self.assertEqual(results[7]["issues"], [98, 99])

    
    def test_prelude_to_knightfall_stories_from(self):

        # Creates a description using the alternative collection phrase
        description = (
            "This volume includes never-before-collected material "
            "in stories from BATMAN: VENGEANCE OF BANE #1, "
            "BATMAN #484-491 and DETECTIVE COMICS #654-658."
        )

        # Extracts the collected comic issues
        results = extract_issues(description)

        # Defines the expected series and issue numbers
        expected = [
            {
                "series": "BATMAN: VENGEANCE OF BANE",
                "issues": [1]
            },
            {
                "series": "BATMAN",
                "issues": list(range(484, 492))
            },
            {
                "series": "DETECTIVE COMICS",
                "issues": list(range(654, 659))
            }
        ]

        # Checks that all three series are correctly identified
        self.assertEqual(results, expected)




if __name__ == "__main__":

    # Run all tests in this file
    unittest.main()