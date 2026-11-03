import os
import requests
from dotenv import load_dotenv
from issue_parser import extract_issues
import time

# Load environment variables from the .env file.
load_dotenv()

def get_book_info(isbn):
    """
    Retrieves book information from the Google Books API.

    Automatically retries requests when Google returns
    temporary server errors.
    """

    url = "https://www.googleapis.com/books/v1/volumes"

    # Configure the Google Books API request.
    params = {
        "q": f"isbn:{isbn}",
        "key": os.environ["GOOGLE_BOOKS_API_KEY"],
        "country": "GB"
    }

    # Attempt the request a maximum of three times.
    for attempt in range(3):

        response = requests.get(url, params=params, timeout=10)

        # Retry when Google encounters a temporary server error.
        if response.status_code in (502, 503, 504):

            if attempt < 2:
                print("\nGoogle Books temporarily unavailable. Retrying...")

                # Increase the delay between attempts.
                time.sleep(2 ** attempt)

                continue

        # Handle unsuccessful Google Books API responses.
        if response.status_code != 200:

            # Attempt to retrieve the API's error information.
            try:
                error_data = response.json().get("error", {})

                # Retrieve the general error status.
                error_status = error_data.get("status", "Unknown")

                # Retrieve the specific error reason when available.
                errors = error_data.get("errors", [])

                error_reason = (
                    errors[0].get("reason", "Unknown")
                    if errors else "Unknown"
                )

            # Handle responses that do not contain valid JSON.
            except ValueError:
                error_status = "Unknown"
                error_reason = "Unknown"

            # Raise an error without exposing the API key.
            raise RuntimeError(
                f"Google Books lookup failed "
                f"(HTTP {response.status_code}). "
                f"Status: {error_status}. "
                f"Reason: {error_reason}."
            )

        # Convert the API response into a dictionary.
        data = response.json()

        # Check whether any matching books were found.
        if not data.get("items"):
            return None

        # Retrieve the first matching book.
        book = data["items"][0]["volumeInfo"]

        return {
            "title": book.get("title", "Unknown"),
            "subtitle": book.get("subtitle", ""),
            "publisher": book.get("publisher", "Unknown"),
            "description": book.get("description", "")
        }

def display_book_info(book):
    """
    Displays the book's information and collected issues.

    Returns False if the description is missing or
    contains no recognisable collected issues.
    """

    # Display the book's metadata.
    print(f"\nTitle: {book['title']}")

    if book["subtitle"]:
        print(f"Subtitle: {book['subtitle']}")

    print(f"Publisher: {book['publisher']}")

    # Check whether the description exists.
    if not book["description"]:
        print("\nNo description is available for this book.")
        return False

    # Extract the collected issues.
    results = extract_issues(book["description"])

    # Check whether any issues were identified.
    if not results:
        print("\nUnable to identify collected issues from the description.")
        return False

    # Display the collected issues.
    print("\nCollected Issues:")

    for result in results:

        print(f"\n{result['series']}")

        for issue in result["issues"]:
            print(f"  #{issue}")

    return True


def main():
    """
    Allows the user to repeatedly search for collected
    editions using their ISBNs.
    """

    print("=== Comic Reader ===")

    while True:

        # Request an ISBN from the user.
        isbn = input("\nEnter ISBN (or Q to quit): ").strip()

        # Allow the user to exit the application.
        if isbn.lower() == "q":
            print("\nExiting Comic Reader.")
            break

        # Prevent empty inputs.
        if not isbn:
            print("Please enter a valid ISBN.")
            continue

        try:
            # Retrieve the book's metadata.
            book = get_book_info(isbn)

        except requests.exceptions.RequestException:
            print("\nUnable to connect to Google Books. Please try again.")
            continue

        except RuntimeError as error:
            print(f"\n{error}")
            continue

        # Handle ISBNs that Google Books cannot identify.
        if not book:
            print("\nNo book found for that ISBN.")
            continue

        # Display the book's information and collected issues.
        success = display_book_info(book)

        if not success:
            print("\nPlease try another ISBN.")


if __name__ == "__main__":
    main()