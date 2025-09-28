from PIL import Image, ImageDraw, ImageFont

class CenteredTextImage:
    def __init__(
        self, 
        font_path="arial.ttf", 
        font_size=100, 
        output_path="output.png", 
        background_path="", 
        font_fill="black", 
        logo_image_path="", 
        logo_size=(500, 500)
    ):
        """
        Initializes the CenteredTextImage class with the image properties and font details.

        Args:
            font_path (str): Path to the .ttf font file (default: Arial).
            font_size (int): Font size for the text (default: 100).
            output_path (str): File path to save the generated image.
            background_path (str): Path to the background image.
            font_fill (str): Color of the font.
            logo_image_path (str): Path to the logo image.
            logo_size (tuple): Size of the logo image.
        """
        self.font_path = font_path
        self.font_size = font_size
        self.fill = font_fill
        self.output_path = output_path
        self.logo_image_path = logo_image_path
        self.logo_size = logo_size

        try:
            self.logo_image = Image.open(self.logo_image_path).convert("RGBA").resize(self.logo_size)
        except FileNotFoundError:
            self.logo_image = None

        self.background_image = Image.open(background_path).convert("RGBA")
        self.image_size = self.background_image.size
        self.draw = ImageDraw.Draw(self.background_image)

        try:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        except OSError:
            raise ValueError("Font file not found. Please provide a valid font path.")

    def split_text_into_lines(self, text):
        """
        Splits a paragraph into lines that fit within the image width.

        Args:
            text (str): The paragraph to split.

        Returns:
            list: A list of lines that fit within the specified image width.
        """
        lines = []
        words = text.split()
        current_line = ""
        max_line_width = self.image_size[0] - 200  # Leave some padding around the text

        for word in words:
            if self.draw.textlength(current_line + " " + word, font=self.font) > max_line_width:
                lines.append(current_line.strip())
                current_line = word
            else:
                current_line += " " + word
        lines.append(current_line.strip())
        return lines

    def calculate_position(self, alignment, text_block_size):
        """
        Calculates the position based on the alignment preference.

        Args:
            alignment (str): Alignment preference ("centered", "left", "right", "top", "bottom").
            text_block_size (tuple): Width and height of the text block.

        Returns:
            tuple: The (x, y) coordinates for the text.
        """
        text_width, text_height = text_block_size
        image_width, image_height = self.image_size

        if alignment == "centered":
            x = (image_width - text_width) // 2
            y = (image_height - text_height) // 2
        elif alignment == "left":
            x = 50  # Padding from the left edge
            y = (image_height - text_height) // 2
        elif alignment == "right":
            x = image_width - text_width - 50  # Padding from the right edge
            y = (image_height - text_height) // 2
        elif alignment == "top":
            x = (image_width - text_width) // 2
            y = 50  # Padding from the top edge
        elif alignment == "bottom":
            x = (image_width - text_width) // 2
            y = image_height - text_height - 50  # Padding from the bottom edge
        else:
            raise ValueError("Invalid alignment. Choose from 'centered', 'left', 'right', 'top', or 'bottom'.")

        return x, y

    def create_image_with_text(self, text, alignment="centered"):
        """
        Creates an image with the provided text and saves it.

        Args:
            text (str): The text to write on the image.
            alignment (str): Alignment preference (default: "centered").
        """
        lines = self.split_text_into_lines(text)
        line_height = self.font.getbbox("A")[3] + 10  # Add some spacing between lines
        block_height = len(lines) * line_height
        block_width = max(self.draw.textlength(line, font=self.font) for line in lines)

        x_start, y_start = self.calculate_position(alignment, (block_width, block_height))

        for line in lines:
            line_width = self.draw.textlength(line, font=self.font)
            x_start_line = x_start if alignment != "centered" else (self.image_size[0] - line_width) // 2
            self.draw.text((x_start_line, y_start), line, fill=self.fill, font=self.font)
            y_start += line_height  # Move to the next line

        self.background_image.save(self.output_path)
        self.background_image.show()
        print(f"Image saved to {self.output_path}")

# Example Usage
image_creator = CenteredTextImage(
    font_path="arial.ttf",
    background_path="save1.png",
    font_fill="white",
    logo_image_path="Images/logo.png",
    font_size=30,
)

paragraph = "Hello world, this is an example of dynamically aligned text."
image_creator.create_image_with_text(paragraph, alignment="left")
