import cv2
import numpy as np


def content_aware_fill(image_path, mask_path, output_path):
    """
    Perform content-aware fill on the specified region in an image.

    :param image_path: Path to the input image.
    :param mask_path: Path to the binary mask indicating the area to be filled (white = area to fill, black = keep).
    :param output_path: Path to save the output image.
    """
    # Load the image and mask
    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, 0)  # Load mask as grayscale

    if image is None or mask is None:
        print("Error: Could not load the image or mask.")
        return

    # Perform inpainting (content-aware fill)
    inpainted_image = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # Save the output
    cv2.imwrite(output_path, inpainted_image)
    print(f"Content-aware fill completed. Output saved to {output_path}")


# Example Usage
image_path = "Images/logo_remover_test.jpg"  # Path to your image
mask_path = "Images/logo_remover_test_mask.png"  # Path to your mask (white region to remove)
output_path = "output_image5.jpg"  # Path to save the result

content_aware_fill(image_path, mask_path, output_path)
