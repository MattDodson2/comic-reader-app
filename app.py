import requests
import streamlit as st

from book_lookup import get_book_info
from issue_parser import extract_issues
from barcode_scanner import scan_isbn

# Caches book information to prevent unnecessary API requests
@st.cache_data(ttl=3600)
def cached_book_lookup(isbn):

    # Retrieves the book's information from Google Books
    return get_book_info(isbn)


# Configures the application's browser tab and page layout
st.set_page_config(
    page_title="Comic Reader",
    page_icon="📚",
    layout="centered"
)

# Displays the application's title and description
st.title("Comic Reader")
st.write("Find the individual comic issues contained in a collected edition.")


# Displays the barcode scanning section
st.subheader("Scan a Barcode")

# Initialises the scanned ISBN
scanned_isbn = None

# Allows the user to upload or capture a barcode photograph
camera_image = st.file_uploader(
    "Take or upload a picture of the book's ISBN barcode",
    type=["jpg", "jpeg", "png"]
)

# Processes the captured image
if camera_image is not None:

    try:
        # Attempts to identify the ISBN
        scanned_isbn = scan_isbn(camera_image)

    # Handles images that cannot be processed
    except (OSError, ValueError):
        st.error("Unable to process the image. Please try again.")

    else:
        # Displays the ISBN if successfully identified
        if scanned_isbn:
            st.success(f"ISBN identified: {scanned_isbn}")

        else:
            st.warning(
                "Unable to identify an ISBN. "
                "Please try taking another picture."
            )


# Separates the two search methods
st.divider()

# Displays the manual ISBN search section
st.subheader("Search by ISBN")

# Creates a form for entering an ISBN
with st.form("isbn_search"):

    # Allows the user to enter an ISBN
    manual_isbn = st.text_input("Enter ISBN:")

    # Creates a button to submit the ISBN
    submitted = st.form_submit_button("Search")

# Prioritises manually submitted ISBNs
if submitted:
    isbn = manual_isbn.strip()

# Uses the scanned ISBN if no manual search was submitted
elif scanned_isbn:
    isbn = scanned_isbn.strip()

# No ISBN has been provided
else:
    isbn = None

# Processes the ISBN when one is available
if isbn is not None:

    # Checks whether the user entered an ISBN
    if not isbn:
        st.warning("Please enter an ISBN.")

    else:

        try:
            # Retrieves the book's information from Google Books
            book = cached_book_lookup(isbn)

        # Handles network and API errors
        except (requests.exceptions.RequestException, RuntimeError):
            st.error(
                "Unable to retrieve book information. "
                "Please try again."
            )

        else:

            # Checks whether Google Books identified the book
            if not book:
                st.warning("No book found for that ISBN. Please try another.")

            else:

                # Displays the book's title
                st.subheader(book["title"])

                # Display which database supplied the book information
                st.caption(f"Data source: {book.get('source', 'Unknown')}")

                # Displays the subtitle when available
                if book["subtitle"]:
                    st.write(book["subtitle"])

                # Displays the publisher
                st.write(f"**Publisher:** {book['publisher']}")

                # Checks whether the book has a description
                if not book["description"].strip():
                    st.warning(
                        "No description is available for this book. "
                        "Please try another ISBN."
                    )

                else:

                    # Extracts the collected issues
                    results = extract_issues(book["description"])

                    # Checks whether any collected issues were identified
                    if not results:
                        st.warning(
                            "Unable to identify collected issues. "
                            "Please try another ISBN."
                        )

                    else:

                        # Displays the collected issues heading
                        st.subheader("Collected Issues")

                        # Displays each identified comic series
                        for result in results:

                            # Retrieves the identified comic series name
                            series_name = result["series"]

                            # Labels collections containing selected stories
                            if result.get("partial"):
                                series_name += " (selected stories)"

                            # Displays the comic series name
                            st.write(f"**{series_name}**")

                            # Formats the individual issue numbers
                            issues = ", ".join(
                                f"#{issue}" for issue in result["issues"]
                            )

                            # Displays the issue list
                            st.write(issues)