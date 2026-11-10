
import re


def expand_issue_range(start, end=None):
    """
    Converts an issue number or range into a list of integers.
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
    from a collected edition's description.
    """

    # Identifies phrases introducing collected issues
    section_pattern = (
        r"\b(?:collects|collecting|"
        r"originally published in single magazine form as)\s+"
    )

    # Searches the description for the collection statement
    section_match = re.search(
        section_pattern,
        description,
        re.IGNORECASE
    )

    # Returns an empty list when no collection statement exists
    if not section_match:
        return []

    # Extracts the text following the collection phrase
    collected_text = description[section_match.end():]

    # Protects volume abbreviations from sentence splitting
    collected_text = re.sub(
        r"\bvol\.(?=\s*\d+\s*\))",
        "vol<DOT>",
        collected_text,
        flags=re.IGNORECASE
    )

    # Keeps the collection statement up to its ending full stop
    collected_text = re.split(
        r"\.(?=\s|$)",
        collected_text,
        maxsplit=1
    )[0]

    # Restores the original volume abbreviations
    collected_text = collected_text.replace("<DOT>", ".")

    # Identifies issues with a hash or an unprefixed range
    issue_pattern = re.compile(
        r"(?<!\w)#\s*(\d+)"
        r"(?:\s*[-–]\s*(\d+))?(?!\w)"
        r"|"
        r"(?<![\w#])(\d+)\s*[-–]\s*(\d+)(?!\w)"
    )

    # Initialises the collection results
    results = []

    # Stores the current series and previous match position
    current_series = None
    previous_end = 0

    # Tracks whether the description refers to selected stories
    partial_collection = False

    # Processes each issue reference in the description
    for match in issue_pattern.finditer(collected_text):

        # Retrieves the text before the current issue reference
        preceding_text = collected_text[
            previous_end:match.start()
        ]

        # Checks whether the description introduces selected stories
        if re.search(
            r"\bstories?\s+from\b",
            preceding_text,
            re.IGNORECASE
        ):
            partial_collection = True

        # Removes surrounding punctuation and whitespace
        series = preceding_text.strip(" \t\n,;:")

        # Removes connecting words from the beginning
        series = re.sub(
            r"^(?:and|or)\b\s*",
            "",
            series,
            flags=re.IGNORECASE
        )

        # Removes wording introducing selected stories
        series = re.sub(
            r"^stories?\s+from\s+",
            "",
            series,
            flags=re.IGNORECASE
        )

        # Removes publication years while preserving volume numbers
        series = re.sub(
            r"\s*\((?:18|19|20)\d{2}\)",
            "",
            series
        ).strip()

        # Creates a new series when a title is identified
        if series:

            current_series = {
                "series": series,
                "issues": []
            }

            # Marks series containing selected stories
            if partial_collection:
                current_series["partial"] = True

            # Adds the new series to the collection
            results.append(current_series)

        # Adds the issue numbers to the current series
        if current_series is not None:

            # Retrieves the issue range from the matching groups
            if match.group(1) is not None:
                start = match.group(1)
                end = match.group(2)

            else:
                start = match.group(3)
                end = match.group(4)

            # Expands and adds the collected issue numbers
            current_series["issues"].extend(
                expand_issue_range(start, end)
            )

        # Stores the ending position of the current match
        previous_end = match.end()

    # Removes duplicate issues and sorts each series
    for result in results:
        result["issues"] = sorted(set(result["issues"]))

    # Returns the identified comic series and issues
    return results