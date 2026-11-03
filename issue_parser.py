import re


def expand_issue_range(start, end=None):
    
    #Converts an issue number or range into a list of integers.

    start = int(start)

    if end is None:
        end = start
    else:
        end = int(end)

    # Rejects invalid or excessively large ranges.
    if start > end or end - start > 1000:
        return []

    return list(range(start, end + 1))


def extract_issues(description):

    # Identifies the beginning of the collected issues statement.
    section_pattern = (
        r"\b(?:collects|collecting|"
        r"originally published in single magazine form as)\s+"
    )

    section_match = re.search(
        section_pattern,
        description,
        re.IGNORECASE
    )

    if not section_match:
        return []

    # Extracts the collected issues statement.
    collected_text = description[section_match.end():].split(".", 1)[0]

    # Removes publication years immediately preceding issue numbers.
    collected_text = re.sub(
        r"\((?:18|19|20)\d{2}\)(?=\s+#?\d)",
        "",
        collected_text
    )

    # Identifies individual issue numbers and ranges.
    issue_pattern = (
        r"(?<![\w])#?(\d+)"
        r"(?:\s*[-–]\s*(\d+))?"
        r"(?!\w)"
    )

    results = []

    # Tracks the current series and our position in the description.
    current_series = None
    previous_end = 0

    for match in re.finditer(issue_pattern, collected_text):

        # Extracts text preceding the current issue reference.
        preceding_text = collected_text[previous_end:match.start()]

        # Removes separators and connecting words.
        series = re.sub(r"^[\s,;:]+", "", preceding_text)

        series = re.sub(
            r"^(?:and|or)\b\s*",
            "",
            series,
            flags=re.IGNORECASE
        )

        series = series.strip(" ,;:")

        # If a series title exists, begin tracking a new series.
        if series:

            # Ignores references that do not contain a series name.
            if not re.search(r"[A-Za-z]", series):
                previous_end = match.end()
                continue

            current_series = {
                "series": series,
                "issues": []
            }

            results.append(current_series)

        # Adds the issue numbers to the current series.
        if current_series is not None:

            start = match.group(1)
            end = match.group(2)

            issues = expand_issue_range(start, end)

            current_series["issues"].extend(issues)

        # Remembers where this issue reference ended.
        previous_end = match.end()

    # Removes duplicate issues and sort each issue list.
    for result in results:
        result["issues"] = sorted(set(result["issues"]))

    return results

if __name__ == "__main__":

    descriptions = [
        "Collects Batman #404-407.",

        "Collects Batman #404-407, Detective Comics #575-578.",

        "Collects Batman #404-407, #410, and #412.",

        "Originally published in single magazine form as "
        "BATMAN: SHADOW OF THE BAT 1-12.",

        "Collects Batman #404-407, #410, Detective Comics #575-578, "
        "and Batman Annual #11.",

        "Collects Batman #404-407 and Detective Comics #575-578.",

        "Collects Batman #404-407, #410, and #412, "
        "Detective Comics #575-578 and Batman Annual #11."
    ]

    for description in descriptions:

        print(f"\nDescription: {description}")

        results = extract_issues(description)

        for result in results:
            print(result)