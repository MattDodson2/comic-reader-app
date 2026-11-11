
import re


def expand_issue_range(start, end=None):
    """
    Converts an issue number or range into a list of integers
    """

    # Converts the starting issue to an integer
    start = int(start)

    # Uses the starting issue when no ending issue exists
    end = int(end) if end is not None else start

    # Rejects invalid or excessively large issue ranges
    if start > end or end - start > 1000:
        return []

    # Returns every issue number in the range
    return list(range(start, end + 1))


def extract_issues(description):
    """
    Extracts comic series titles and issue numbers
    from a collected edition's description
    """

    # Identifies phrases introducing collected issues
    section_pattern = (
        r"\b(?:collects|collecting|colles|"
        r"originally published in single magazine form "
        r"(?:as|in))\s*:?\s*"
    )

    # Searches for the collected-issues statement
    section_match = re.search(
        section_pattern,
        description,
        re.IGNORECASE
    )

    # Returns an empty list when no statement is found
    if not section_match:
        return []

    # Retrieves the text following the collection phrase
    collected_text = description[section_match.end():]

    # Identifies descriptions placing issue numbers before the title
    reverse_pattern = (
        r"^issues?\s+#?(\d+)"
        r"(?:\s*[-–]\s*#?(\d+))?"
        r"\s+of\s+([^,.;]+)"
    )

    # Searches for the alternative description format
    reverse_match = re.search(
        reverse_pattern,
        collected_text,
        re.IGNORECASE
    )

    # Processes descriptions with issue numbers before the title
    if reverse_match:

        # Expands the identified issue range
        issues = expand_issue_range(
            reverse_match.group(1),
            reverse_match.group(2)
        )

        # Rejects an invalid issue range
        if not issues:
            return []

        # Returns the identified series and issues
        return [{
            "series": reverse_match.group(3).strip(),
            "issues": issues
        }]

    # Removes text following the collection statement
    collected_text = re.split(
        r"\.(?=\s+[A-Z]|$)",
        collected_text,
        maxsplit=1
    )[0]

    # Identifies individual issue numbers and ranges
    issue_pattern = re.compile(
        r"(?<![\w'’\-#])#?\s*(\d{1,4})"
        r"(?:\s*[-–]\s*#?\s*(\d{1,4}))?"
        r"(?![\w'’\-])"
    )

    # Initialises the extracted collection results
    results = []

    # Stores the current series being processed
    current_series = None

    # Tracks the ending position of the previous issue reference
    previous_end = 0

    # Tracks whether selected stories are being collected
    partial_collection = False

    # Processes every issue reference in the statement
    for match in issue_pattern.finditer(collected_text):

        # Ignores numbers enclosed in parentheses
        if collected_text[match.end():].lstrip().startswith(")"):
            continue

        # Retrieves the text preceding the current issue reference
        preceding_text = collected_text[
            previous_end:match.start()
        ]

        # Removes surrounding separators and whitespace
        series = preceding_text.strip(" \t\n,;:")

        # Removes connecting words from the beginning
        series = re.sub(
            r"^(?:and|or)\b\s*",
            "",
            series,
            flags=re.IGNORECASE
        ).strip()

        # Checks whether the text introduces selected stories
        if re.match(
            r"^stories?\s+from\b",
            series,
            re.IGNORECASE
        ):

            # Marks subsequent series as partial collections
            partial_collection = True

            # Removes the introductory wording
            series = re.sub(
                r"^stories?\s+from\s+",
                "",
                series,
                flags=re.IGNORECASE
            )

        # Removes publication years from series titles
        series = re.sub(
            r"\s*\((?:18|19|20)\d{2}\)\s*$",
            "",
            series
        ).strip()

        # Creates a new entry when a series title is identified
        if series:

            # Creates the new series dictionary
            current_series = {
                "series": series,
                "issues": []
            }

            # Marks the series when only selected stories are included
            if partial_collection:
                current_series["partial"] = True

            # Adds the new series to the results
            results.append(current_series)

        # Processes the issue reference when a series exists
        if current_series is not None:

            # Expands the issue reference into individual numbers
            issues = expand_issue_range(
                match.group(1),
                match.group(2)
            )

            # Rejects invalid issue references
            if not issues:
                return []

            # Adds the issues to the current series
            current_series["issues"].extend(issues)

        # Stores the ending position of the current reference
        previous_end = match.end()

    # Removes duplicate issues and sorts each series
    for result in results:
        result["issues"] = sorted(set(result["issues"]))

    # Returns the extracted comic series and issues
    return results
