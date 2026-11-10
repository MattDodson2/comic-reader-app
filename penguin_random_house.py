
import os
import re
import html
import requests

from dotenv import load_dotenv


# Load the API key from the .env file
load_dotenv()


def find_flap_copy(data):
    """
    Finds flap copy within the PRH API response.
    """

    # Search dictionaries for the flap copy field
    if isinstance(data, dict):

        for key, value in data.items():

            # Standardise the field name
            field_name = re.sub(r"[^a-z]", "", key.lower())

            # Check whether the field contains flap copy
            if field_name == "flapcopy":

                if isinstance(value, str):
                    return value

                # Handle flap copy stored inside another object
                if isinstance(value, dict):
                    for field in ("value", "text", "content", "html"):
                        text = value.get(field)

                        if isinstance(text, str):
                            return text

        # Search nested dictionaries and lists
        for value in data.values():
            result = find_flap_copy(value)

            if result:
                return result

    # Search each item within a list
    elif isinstance(data, list):

        for item in data:
            result = find_flap_copy(item)

            if result:
                return result

    # Return an empty string when no flap copy exists
    return ""


def clean_description(description):
    """
    Removes HTML formatting from book descriptions.
    """

    # Remove HTML tags from the description
    description = re.sub(r"<[^>]+>", " ", description)

    # Convert HTML character references into readable text
    description = html.unescape(description)

    # Remove unnecessary whitespace
    return " ".join(description.split())



def find_title_record(data, isbn):
    """
    Finds the matching ISBN record within a PRH response.
    """

    # Checks whether the current object is a dictionary
    if isinstance(data, dict):

        # Retrieves the title and ISBN fields
        title = data.get("title")
        record_isbn = data.get("isbn")

        # Checks whether the object contains a valid book title
        if isinstance(title, str) and title.strip():

            # Checks whether the ISBN matches the requested edition
            if record_isbn is None or str(record_isbn) == str(isbn):
                return data

        # Searches nested objects for the matching book record
        for value in data.values():
            result = find_title_record(value, isbn)

            # Returns the record when a match is found
            if result is not None:
                return result

    # Checks whether the current object is a list
    elif isinstance(data, list):

        # Searches each item in the list
        for item in data:
            result = find_title_record(item, isbn)

            # Returns the record when a match is found
            if result is not None:
                return result

    # Returns None when no matching record is found
    return None


def get_prh_book_info(isbn):
    """
    Retrieves book metadata and flap copy from PRH.
    """

    # Retrieve the PRH API key
    api_key = os.environ.get("PRH_API_KEY")

    # Check whether the API key is configured
    if not api_key:
        raise RuntimeError("PRH_API_KEY is not configured.")

    # Define the API endpoint for the supplied ISBN
    url = (
        "https://api.penguinrandomhouse.com"
        f"/resources/v2/title/domains/PRH.US/titles/{isbn}"
    )

    # Configure the API request parameters
    params = {"api_key": api_key}

    # Retrieve the book's metadata.
    response = requests.get(url, params=params, timeout=15)

    # Return None when PRH cannot identify the book
    if response.status_code == 404:
        return None

    # Handle unsuccessful requests
    if not response.ok:
        raise RuntimeError(
            f"PRH lookup failed (HTTP {response.status_code})."
        )

    # Searches the API response for the requested edition
    title_data = find_title_record(response.json(), isbn)

    # Checks whether valid title metadata was found
    if title_data is None:
        raise ValueError("Unable to identify the PRH title record.")

    # Retrieve additional book content
    content_response = requests.get(
        f"{url}/content",
        params=params,
        timeout=15
    )

    # Handle a missing content record
    if content_response.status_code == 404:
        content_data = {}

    elif not content_response.ok:
        raise RuntimeError(
            f"PRH content lookup failed "
            f"(HTTP {content_response.status_code})."
        )

    else:
        content_data = content_response.json()

    # Extract the book's flap copy
    description = find_flap_copy(content_data)

    # Check the title response if the content has no flap copy
    if not description:
        description = find_flap_copy(title_data)

    # Remove HTML formatting from the description
    description = clean_description(description)

    # Retrieves the publisher or imprint information
    publisher = (
        title_data.get("consumerImprint")
        or title_data.get("publisher")
        or title_data.get("imprint")
        or "Unknown"
    )

    # Extracts the publisher name when stored as a dictionary
    if isinstance(publisher, dict):
        publisher = (
            publisher.get("description")
            or publisher.get("name")
            or "Unknown"
    )

    # Return information in our existing book format
    return {
        "title": title_data.get("title", "Unknown"),
        "subtitle": title_data.get("subtitle") or "",
        "publisher": publisher,
        "description": description,
        "source": "Penguin Random House"
    }
