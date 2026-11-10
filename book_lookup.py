
import os
import requests

from isbn_lookup import get_book_info as get_google_book_info
from penguin_random_house import get_prh_book_info


def get_book_info(isbn):
    """
    Retrieves book information using PRH as the primary source
    and Google Books as a fallback.
    """

    # Ensures the primary API has been configured
    if not os.environ.get("PRH_API_KEY"):
        raise RuntimeError("PRH_API_KEY is not configured.")

    # Initialises the primary result and error state
    prh_book = None
    prh_failed = False

    try:
        # Attempts to retrieve the book from PRH
        prh_book = get_prh_book_info(isbn)

    # Allows Google Books to be used if PRH is unavailable
    except (requests.exceptions.RequestException, RuntimeError, ValueError):
        prh_failed = True

    # Uses PRH when it supplies a description
    if prh_book and prh_book.get("description", "").strip():
        return prh_book

    try:
        # Attempts to retrieve the book from Google Books
        google_book = get_google_book_info(isbn)

    # Handles errors from the fallback API
    except (requests.exceptions.RequestException, RuntimeError):

        # Returns available PRH metadata if possible
        if prh_book:
            return prh_book

        # Reports that book retrieval failed
        raise RuntimeError("Unable to retrieve book information.")

    # Returns Google Books data when available
    if google_book:
        google_book["source"] = "Google Books (fallback)"
        return google_book

    # Preserves incomplete PRH records when Google has no match
    if prh_book:
        return prh_book

    # Distinguishes service failure from an unknown ISBN
    if prh_failed:
        raise RuntimeError("PRH unavailable and no Google Books record found.")

    # Neither database was able to identify the book
    return None
