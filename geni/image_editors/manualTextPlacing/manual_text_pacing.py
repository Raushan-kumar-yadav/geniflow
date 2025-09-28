from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_image(size, bgColor='white', message='Hello World', font_path='arial.ttf', fontColor='black', font_size=20):
    W, H = size
    image = Image.new('RGB', size, bgColor)
    draw = ImageDraw.Draw(image)
    try:
        with open('test.txt', 'r') as file:
            my_text = file.read()  # Read and strip extra spaces/newlines
    except FileNotFoundError:
        print("Error: 'test.txt' not found.")
        my_text = "Default Text"

    # Load the font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        print(f"Error: Font '{font_path}' not found.")
        return None

    """     # Handle multiline text wrapping
    max_width = W - 40  # Leave some padding
    wrapped_text = textwrap.fill(message, width=40)  # Adjust the width as needed """

    # Calculate text size
    _, _, w, h = draw.textbbox((0, 0), my_text, font=font)

    # Draw the centered text
    draw.multiline_text(((W -1020), (H - h) / 2), my_text, font=font, fill=fontColor,align="center")
    return image

# Parameters
my_font_path = 'arial.ttf'  # Update with your font path
try:
    with open('test.txt', 'r') as file:
        my_text = file.read()  # Read and strip extra spaces/newlines
except FileNotFoundError:
    print("Error: 'test.txt' not found.")
    my_text = "Default Text"

my_font_color = 'black'
my_bgcolor = 'white'

# Create the image
my_image = create_image(
    size=(1080, 1080), 
    bgColor=my_bgcolor, 
    message=my_text, 
    font_path=my_font_path, 
    fontColor=my_font_color,
    font_size=40  # Adjust font size
)

# Save and display the image
if my_image:
    my_image.show()
    my_image.save('output_image.png', 'PNG')
