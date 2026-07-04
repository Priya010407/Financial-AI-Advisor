import easyocr
from PIL import Image
import numpy as np

# Initialize the OCR reader once (English)
reader = easyocr.Reader(['en'], gpu=False)

def extract_text(uploaded_file):
    """
    Extract text from an uploaded image using EasyOCR.
    """

    try:
        # Open image
        image = Image.open(uploaded_file)

        # Convert image to numpy array
        image_np = np.array(image)

        # Perform OCR
        result = reader.readtext(image_np, detail=0)

        # Join detected text into one string
        text = "\n".join(result)

        return text

    except Exception as e:
        return f"Error while reading image: {e}"