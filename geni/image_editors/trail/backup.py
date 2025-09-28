from PIL import Image, ImageDraw, ImageFont
import linecache

class CenteredTextImage:
    Task_completed = False  # This is going to control while loop

    def __init__(self, font_path="arial.ttf", font_size=100, output_path="output.png", background_path="", font_fill="black", logo_image_path="", logo_size=(500, 500)):
        """
        Initializes the CenteredTextImage class with the image properties and font details.

        Args:
            image_size (tuple): Width and height of the image (default: 800x600).
            font_path (str): Path to the .ttf font file (default: Arial).
            font_size (int): Font size for the text (default: 30).
            output_path (str): File path to save the generated image (default: "output.png").
        """
        self.font_path = font_path
        self.font_size = font_size
        self.fill = font_fill
        self.output_path = output_path
        self.logo_image_path = logo_image_path
        self.logo_image = Image.open(self.logo_image_path, 'r').convert("RGBA").resize(logo_size)
        self.background_image = Image.open(background_path, 'r').convert("RGBA")
        self.image_size = self.background_image.size
        self.draw = ImageDraw.Draw(self.background_image)
        try:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        except OSError:
            raise ValueError("Font file not found. Please provide a valid font path.")

    def process_paragraph(self, paragraph):
        """
        Processes the paragraph to extract text up to the first blank line.

        Args:
            paragraph (str): The input string containing the paragraph.

        Returns:
            str: The processed paragraph up to the first blank line.
        """
        lines = paragraph.split("\n")  # Split paragraph into lines
        result = []
        blank_line_count = 0

        for line in lines:
            if line.strip() == "":
                blank_line_count += 1
                if blank_line_count == 2:
                    # Two consecutive blank lines stop the program
                    print("Two consecutive blank lines detected. Program stopping.")
                    CenteredTextImage.Task_completed = True
                    break
                elif blank_line_count == 1:
                    # Stop appending further lines, but program continues
                    print("Blank line detected. Stop taking input but program continues.")
                    break
            else:
                blank_line_count = 0  # Reset counter for non-blank lines
                result.append(line.strip())

        return " ".join(result)

    def number_of_line_in_selected_para(self, text):
        # This function going to count number of lines in selected paragraph and seeking the cursor to next line
        number_of_lines = text.splitlines()  # Split the string into lines
        line_count = len(number_of_lines)  # Count the lines
        print(line_count)
        return line_count

    def seek_cursor_to_next_line(self, text, number_of_line_to_seek):
        # This function use the number_of_line_in_selected_para function and move Cursor to next line
        line = linecache.getline(text, number_of_line_to_seek)  # Get the line
        return line

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

    def add_logo(self):
        self.background_image.paste(self.logo_image, (200, 850), self.logo_image)

    def create_image_with_text(self, text, position=None):
        """
        Creates an image with the provided centered text and saves it.

        Args:
            text (str): The text to write on the image.
            position (tuple): The position (x, y) where text should be centered.
        """
        lines = self.split_text_into_lines(text)
        line_height = self.font.getbbox("A")[3] + 10  # Add some spacing between lines
        block_height = len(lines) * line_height

        if position is None:
            # Default to vertically centered position
            x_start = (self.image_size[0] - self.draw.textlength(lines[0], font=self.font)) // 2
            y_start = (self.image_size[1] - block_height) // 2
        else:
            x_start, y_start = position  # Use user-defined position

        for line in lines:
            line_width = self.draw.textlength(line, font=self.font)
            x_start_line = (self.image_size[0] - line_width) // 2  # Center the line horizontally
            self.draw.text((x_start_line, y_start), line, fill=self.fill, font=self.font)
            y_start += line_height  # Move to the next line

        self.background_image.save(self.output_path)
        self.background_image.show()
        print(f"Image saved to {self.output_path}")

# Example usage
with open("test.txt", "r") as file:
    paragraph = "".join(file.readlines())

print(paragraph)

# Create an instance of the class
image_creator = CenteredTextImage(font_path="Movistar Text Regular.ttf", background_path="bg.png", font_fill="black", logo_image_path="logo.png", font_size=30)

processed_paragraph = image_creator.process_paragraph(paragraph)
print(processed_paragraph)
number_of_line_in_selected_para = image_creator.number_of_line_in_selected_para(processed_paragraph)
image_creator.seek_cursor_to_next_line(processed_paragraph, number_of_line_in_selected_para)
image_creator.add_logo()

# Allow the user to specify the position
user_position = (500,400)  # Example position (x, y)
image_creator.create_image_with_text(processed_paragraph, position=user_position)
