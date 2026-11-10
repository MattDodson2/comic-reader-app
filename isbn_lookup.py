import os
import requests
from dotenv import load_dotenv
from issue_parser import extract_issues
import time

# Loads environment variables from the .env file
load_dotenv()

def get_book_info(isbn):
    """
    Retrieves book information from the Google Books API.

    Automatically retries requests when Google returns
    temporary server errors.
    """

    # Defines the Google Books API endpoint
    url = "https://www.googleapis.com/books/v1/volumes"

    # Configures the API request parameters
    params = {
        "q": f"isbn:{isbn}",
        "key": os.environ["GOOGLE_BOOKS_API_KEY"]
    }

    # Attempts the request a maximum of three times
    for attempt in range(3):

        # Sends the request to Google Books
        response = requests.get(url, params=params, timeout=10)

        # Checks whether Google returned a temporary server error
        if response.status_code in (502, 503, 504):

            # Retries if the maximum number of attempts has not been reached
            if attempt < 2:

                # Waits before sending another request
                time.sleep(2 ** attempt)

                # Continues to the next attempt
                continue

        # Handles unsuccessful API responses
        if response.status_code != 200:
            raise RuntimeError(
                f"Google Books lookup failed (HTTP {response.status_code})."
            )

        # Converts the JSON response into a Python dictionary
        data = response.json()

        # Returns None if no matching books were found
        if not data.get("items"):
            return None

        # Retrieves the first matching book
        book = data["items"][0]["volumeInfo"]

        # Returns the book's information
        return {
            "title": book.get("title", "Unknown"),
            "subtitle": book.get("subtitle", ""),
            "publisher": book.get("publisher", "Unknown"),
            "description": book.get("description", "")
        }

def display_book_info(book):

    # Displays the book's metadata
    print(f"\nTitle: {book['title']}")

    if book["subtitle"]:
        print(f"Subtitle: {book['subtitle']}")

    print(f"Publisher: {book['publisher']}")

    # Checks whether the description exists
    if not book["description"]:
        print("\nNo description is available for this book.")
        return False

    # Extracts the collected issues
    results = extract_issues(book["description"])

    # Checks whether any issues were identified
    if not results:
        print("\nUnable to identify collected issues from the description.")
        return False

    # Displays the collected issues
    print("\nCollected Issues:")

    for result in results:

        print(f"\n{result['series']}")

        for issue in result["issues"]:
            print(f"  #{issue}")

    return True


def main():

    while True:

        # Requests an ISBN from the user
        isbn = input("\nEnter ISBN (or Q to quit): ").strip()

        # Allows the user to exit the application
        if isbn.lower() == "q":
            print("\nExiting Comic Reader.")
            break

        # Prevents empty inputs
        if not isbn:
            print("Please enter a valid ISBN.")
            continue

        try:
            # Retrieves the book's metadata
            book = get_book_info(isbn)

        except requests.exceptions.RequestException:
            print("\nUnable to connect to Google Books. Please try again.")
            continue

        except RuntimeError as error:
            print(f"\n{error}")
            continue

        # Handles ISBNs that Google Books cannot identify
        if not book:
            print("\nNo book found for that ISBN.")
            continue

        # Displays the book's information and collected issues
        success = display_book_info(book)

        if not success:
            print("\nPlease try another ISBN.")


if __name__ == "__main__":
    main()