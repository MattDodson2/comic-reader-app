import requests
import streamlit as st

from isbn_lookup import get_book_info
from issue_parser import extract_issues
from barcode_scanner import scan_isbn


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

        # Handle network and API errors.
        except (requests.exceptions.RequestException, RuntimeError):
            st.error("Unable to retrieve book information. Please try again.")

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