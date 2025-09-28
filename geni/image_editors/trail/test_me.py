from PIL import Image, ImageDraw, ImageFont
import pandas as pd

def wrap_text_to_image(text, image_size=(1080, 1080), font_path="arial.ttf", font_size=1, left_margin=100,right_margine = 30):
    """
    Wraps the input text into an image with the given dimensions.

    Parameters:
        text (str): The text to wrap and display.
        image_size (tuple): The dimensions of the image (width, height).
        font_path (str): Path to the .ttf font file.
        font_size (int): Font size to use for rendering the text.
        left_margin (int): Margin from the left side of the image.

    Returns:
        Image: An image object with the wrapped text.
    """
    # Create a blank image with a white background
    img = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(img)

    # Load the font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise ValueError("Font file not found. Provide a valid font path.")

    # Calculate line height
    line_height = draw.textbbox((0, 0), "A", font=font)[3] + 5  # Add padding between lines
    max_width = image_size[0] - left_margin - right_margine  # Account for left and right margins
    x, y = left_margin, right_margine  # Starting position for text (including left margin)

    # Wrap the text
    lines = []
    paragraphs = text.split("\n")  # Split text into paragraphs by blank lines

    for paragraph in paragraphs:
        if paragraph.strip():  # If the line is not blank
            words = paragraph.split()
            current_line = []
            for word in words:
                test_line = " ".join(current_line + [word])
                text_width = draw.textbbox((0, 0), test_line, font=font)[2]
                if text_width <= max_width:  # Check if the line fits within the available width
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
        else:
            lines.append("")  # Add a blank line for empty paragraphs

    # Check if the text fits vertically
    if y + len(lines) * line_height > image_size[1]:
        raise ValueError("Text is too long to fit in the image.")

    # Draw each line on the image
    for line in lines:
        if line.strip():  # Non-empty line
            draw.text((x, y), line, font=font, fill="black")
        y += line_height

    return img

df = pd.read_excel("csv/Book1.xlsx")
Text_cell = df.iloc[1,0]  # Get the first cell's content

text = Text_cell
image = wrap_text_to_image(text, font_path="arial.ttf", font_size=100)
image.show()  # Display the image
image.save("wrapped_text_image.png")  # Save the image
