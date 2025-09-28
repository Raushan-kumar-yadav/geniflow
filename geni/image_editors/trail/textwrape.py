from PIL import Image, ImageDraw, ImageFont
import pandas as pd


class DynamicTextDrawer:
    """
    A class to dynamically wrap text and draw it on an image with adjustable font size,
    font path, and font color for each word.
    """

    def __init__(self, image_width, image_height, background_color="white"):
        self.image_width = image_width
        self.image_height = image_height
        self.image = Image.new("RGB", (image_width, image_height), color=background_color)
        self.draw = ImageDraw.Draw(self.image)

    def get_font(self, font_path, font_size):
        """
        Load a font with a specified path and size.
        """
        return ImageFont.truetype(font_path, font_size)

    def wrap_text(self, text, font_details):
        """
        Wrap the text to fit within the image width and prepare word attributes.

        :param text: The input text to wrap.
        :param font_details: A list of dictionaries containing font and color details for each word.
                             Example: [{"font_type": "path_to_font.ttf", "font_size": 40, "color": "red"}, ...]
        :return: A list of wrapped lines, where each line is a list of word attributes.
        """
        max_width = self.image_width - 100  # Account for margins
        wrapped_lines = []
        words = text.split()
        current_line = []

        for word, font_detail in zip(words, font_details):
            font = self.get_font(font_detail["font_type"], font_detail["font_size"])
            word_width = self.draw.textbbox((0, 0), word, font=font)[2]

            # Test if adding the word exceeds the max width
            test_line = current_line + [{"word": word, "font_type": font_detail["font_type"],
                                         "font_size": font_detail["font_size"], "color": font_detail["color"]}]
            test_width = sum(
                self.draw.textbbox((0, 0), w["word"], font=self.get_font(w["font_type"], w["font_size"]))[2]
                + self.draw.textbbox((0, 0), " ", font=font)[2] for w in test_line
            )

            if test_width <= max_width:
                current_line.append({"word": word, "font_type": font_detail["font_type"],
                                     "font_size": font_detail["font_size"], "color": font_detail["color"]})
            else:
                wrapped_lines.append(current_line)
                current_line = [{"word": word, "font_type": font_detail["font_type"],
                                 "font_size": font_detail["font_size"], "color": font_detail["color"]}]

        if current_line:
            wrapped_lines.append(current_line)

        return wrapped_lines
    
    def get_words_per_line(self,wrapped_lines):
        """
        Calculate the number of words in each wrapped line.
    
        :param wrapped_lines: List of wrapped lines with word attributes.
        :return: A list where each element is the number of words in the corresponding line.
        """
        words_per_line = [len(line) for line in wrapped_lines]
        return words_per_line


    def draw_text(self, wrapped_lines, margin=50, line_spacing=10):
        """
        Draw wrapped text on the image with specified font colors.

        :param wrapped_lines: List of wrapped lines with word attributes.
        :param margin: Margin on the left.
        :param line_spacing: Spacing between lines.
        """
        y = margin  # Starting Y position

        for line in wrapped_lines:
            line_height = max(
                self.draw.textbbox((0, 0), word["word"], font=self.get_font(word["font_type"], word["font_size"]))[3]
                for word in line
            )

            x = margin  # Starting X position
            for word in line:
                font = self.get_font(word["font_type"], word["font_size"])
                color = word.get("color", "black")  # Default color is black

                # Draw the word
                self.draw.text((x, y), word["word"], font=font, fill=color)

                # Update X position for the next word, including a space
                word_width = self.draw.textbbox((0, 0), word["word"], font=font)[2]
                space_width = self.draw.textbbox((0, 0), " ", font=font)[2]
                x += word_width + space_width

            # Update Y position for the next line
            y += line_height + line_spacing

        # Display and save the image
        self.image.show()
        self.image.save("wrapped_text_output.png")


# Usage Example
if __name__ == "__main__":
    # Image dimensions
    image_width = 1080
    image_height = 1080

    # Create an instance of DynamicTextDrawer
    dynamic_text = DynamicTextDrawer(image_width, image_height)

    # Sample text and font details
    df = pd.read_excel("csv\Book1.xlsx")
    Text_cell = str(df.iloc[2, 0])

    sample_text = Text_cell
    font_details = [
        {"font_type": "arial.ttf", "font_size": 40, "color": "red"},
        {"font_type": "arialbd.ttf", "font_size": 35, "color": "blue"},
        {"font_type": "arial.ttf", "font_size": 30, "color": "green"},
        {"font_type": "arial.ttf", "font_size": 40, "color": "purple"},
        {"font_type": "arialbd.ttf", "font_size": 35, "color": "orange"},
        {"font_type": "arial.ttf", "font_size": 30, "color": "black"},
        {"font_type": "arial.ttf", "font_size": 40, "color": "pink"},
    ]

    # Wrap text and draw it on the image
    wrapped_lines = dynamic_text.wrap_text(sample_text, font_details)
    print(dynamic_text.get_words_per_line(wrapped_lines))
    dynamic_text.draw_text(wrapped_lines)
