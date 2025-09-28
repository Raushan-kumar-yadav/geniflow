
import cv2

# Load the main image and template in grayscale
main_image = cv2.imread(r"E:\adb_ss\screenshot.png", 0)  # Grayscale
template = cv2.imread(r"C:\Users\raush\OneDrive\Pictures\Screenshots\Screenshot 2025-02-05 163938.png", 0)  # Grayscale

# Validate images are loaded
if main_image is None:
    raise FileNotFoundError("Error: 'output.png' could not be loaded. Ensure the file exists and the path is correct.")
if template is None:
    raise FileNotFoundError("Error: 'logo.png' could not be loaded. Ensure the file exists and the path is correct.")

# Ensure the template is smaller than or equal to the main image
if template.shape[0] > main_image.shape[0] or template.shape[1] > main_image.shape[1]:
    print(f"Template size: {template.shape}, Main image size: {main_image.shape}")
    print("Resizing the template to fit within the main image...")
    scale_x = main_image.shape[1] / template.shape[1]
    scale_y = main_image.shape[0] / template.shape[0]
    scale = min(scale_x, scale_y)  # Keep aspect ratio
    template = cv2.resize(template, (int(template.shape[1] * scale), int(template.shape[0] * scale)))

# Match the template
result = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(result)

# Threshold for a match
threshold = 0.9
if max_val >= threshold:
    print("Template found at:", max_loc)
else:
    print("Template not found.")
