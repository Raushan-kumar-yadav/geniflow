import pprint
from PIL import Image
import pytesseract
from regex import T
from sympy import true

# Ensure Tesseract OCR is installed and configured on your system
# Example path for Tesseract executable on Windows


def extract_text_from_image(image_path):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    try:
        # Open the image file
        img = Image.open(image_path)

        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(img)
        print(extracted_text)
        if extracted_text:
            return False  
    except Exception as e:
        return True

# Example usage
image_path = "downloaded_image.jpg"  # Replace with your image path
text = extract_text_from_image(image_path)
print(text)

