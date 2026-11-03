import requests
import streamlit as st

from isbn_lookup import get_book_info
from issue_parser import extract_issues
from barcode_scanner import scan_isbn

import os

# Cache book information to prevent unnecessary API requests.
@st.cache_data(ttl=3600)
def cached_book_lookup(isbn):

    # Retrieve the book's information from Google Books.
    return get_book_info(isbn)


# Configure the application's browser tab and page layout.
st.set_page_config(
    page_title="Comic Reader",
    page_icon="📚",
    layout="centered"
)

# Identify the deployed application version.
st.caption("Diagnostic Version 2")

# Create a button to test the Google Books API.
if st.button("Test Google Books Connection"):

    # Retrieve the API key from the environment.
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")

    # Check whether the API key is available.
    if not api_key:
        st.error("Google Books API key is missing.")

    else:

        # Configure a direct request to Google Books.
        url = "https://www.googleapis.com/books/v1/volumes"

        params = {
            "q": "isbn:9781401263195",
            "key": api_key
        }

        try:

            # Send the request directly to Google Books.
            response = requests.get(url, params=params, timeout=10)

            # Display the response's content type.
            st.write(
                "Content Type:",
                response.headers.get("Content-Type", "Unknown")
            )

            # Remove the API key from the response before displaying it.
            safe_response = response.text.replace(api_key, "[REDACTED]")

            # Display the first 500 characters of Google's response.
            st.code(safe_response[:500])

            # Display the HTTP response status.
            st.write(f"HTTP Status: {response.status_code}")

            # Convert the response into a dictionary.
            data = response.json()

            # Retrieve the error information if available.
            error = data.get("error", {})

            # Retrieve the error details.
            details = error.get("details", [])

            # Display the general error status.
            st.write("Google Status:", error.get("status", "Unknown"))

            # Display specific error information.
            for detail in details:

                if detail.get("@type", "").endswith("ErrorInfo"):

                    st.write("Error Reason:", detail.get("reason"))

                    st.write(
                        "Additional Details:",
                        detail.get("metadata", {})
                    )

            # Confirm successful API access.
            if response.status_code == 200:
                st.success("Google Books API connection successful.")

        # Handle connection errors without exposing the API key.
        except requests.exceptions.RequestException:
            st.error("Unable to connect to Google Books.")

        # Handle responses that do not contain valid JSON.
        except ValueError:
            st.error("Google Books returned an unexpected response.")


# Display the application's title and description.
st.title("Comic Reader")
st.write("Find the individual comic issues contained in a collected edition.")


# Display the barcode scanning section.
st.subheader("Scan a Barcode")

# Initialise the scanned ISBN.
scanned_isbn = None

# Allow the user to upload or capture a barcode photograph.
camera_image = st.file_uploader(
    "Take or upload a picture of the book's ISBN barcode",
    type=["jpg", "jpeg", "png"]
)

# Process the captured image.
if camera_image is not None:

    try:
        # Attempt to identify the ISBN.
        scanned_isbn = scan_isbn(camera_image)

    # Handle images that cannot be processed.
    except (OSError, ValueError):
        st.error("Unable to process the image. Please try again.")

    # Display the ISBN if successfully identified.
    if scanned_isbn:
        st.success(f"ISBN identified: {scanned_isbn}")

    else:
        st.warning(
            "Unable to identify an ISBN. "
            "Please try taking another picture."
        )


# Separate the two search methods.
st.divider()

# Display the manual ISBN search section.
st.subheader("Search by ISBN")

# Create a form for entering an ISBN.
with st.form("isbn_search"):

    # Allow the user to enter an ISBN.
    manual_isbn = st.text_input("Enter ISBN:")

    # Create a button to submit the ISBN.
    submitted = st.form_submit_button("Search")


# Prioritise manually submitted ISBNs.
if submitted:
    isbn = manual_isbn.strip()

# Use the scanned ISBN if no manual search was submitted.
elif scanned_isbn:
    isbn = scanned_isbn.strip()

# No ISBN has been provided.
else:
    isbn = None


# Process the ISBN when one is available.
if isbn is not None:

    # Check whether the user entered an ISBN.
    if not isbn:
        st.warning("Please enter an ISBN.")

    else:

        try:
            # Retrieve the book's information from Google Books.
            book = cached_book_lookup(isbn)

        # Handle unsuccessful API responses.
        except RuntimeError as error:
            st.error(f"Google Books API error: {error}")

        # Handle network connection errors.
        except requests.exceptions.RequestException as error:

            # Retrieve the HTTP status code if available.
            response = error.response

            if response is not None:
                st.error(
                    f"Google Books returned HTTP {response.status_code}."
                )

            else:
                st.error(
                    "Unable to connect to Google Books. "
                    "Please check your connection and try again."
                )

        else:

            # Check whether Google Books identified the book.
            if not book:
                st.warning("No book found for that ISBN. Please try another.")

            else:

                # Display the book's title.
                st.subheader(book["title"])

                # Display the subtitle when available.
                if book["subtitle"]:
                    st.write(book["subtitle"])

                # Display the publisher.
                st.write(f"**Publisher:** {book['publisher']}")

                # Check whether the book has a description.
                if not book["description"].strip():
                    st.warning(
                        "No description is available for this book. "
                        "Please try another ISBN."
                    )

                else:

                    # Extract the collected issues.
                    results = extract_issues(book["description"])

                    # Check whether any collected issues were identified.
                    if not results:
                        st.warning(
                            "Unable to identify collected issues. "
                            "Please try another ISBN."
                        )

                    else:

                        # Display the collected issues heading.
                        st.subheader("Collected Issues")

                        # Display each identified comic series.
                        for result in results:

                            # Display the series title.
                            st.write(f"**{result['series']}**")

                            # Format the individual issue numbers.
                            issues = ", ".join(
                                f"#{issue}" for issue in result["issues"]
                            )

                            # Display the issue list.
                            st.write(issues)