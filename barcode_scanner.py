import zxingcpp
from PIL import Image


def scan_isbn(image_file):
    """
    Scans an image for an ISBN-13 barcode and returns
    the ISBN if one is found.
    """

    # Open the supplied image and convert it to RGB.
    image = Image.open(image_file).convert("RGB")

    # Identify all barcodes contained within the image.
    barcodes = zxingcpp.read_barcodes(image)

    # Examine each barcode detected in the image.
    for barcode in barcodes:

        # Retrieve the decoded barcode value.
        barcode_value = barcode.text

        # Check whether the barcode contains an ISBN-13.
        if (
            barcode_value.isdigit()
            and len(barcode_value) == 13
            and barcode_value.startswith(("978", "979"))
        ):

            # Return the identified ISBN.
            return barcode_value

    # Return None if no ISBN was identified.
    return None