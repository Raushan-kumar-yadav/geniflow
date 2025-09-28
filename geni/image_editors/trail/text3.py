from PIL import Image, ImageDraw, ImageFont


class DynamicTextWrapper:
    def __init__(self, image_width, image_height):
        self.image_width = image_width
        self.image_height = image_height
        self.image = Image.new("RGB", (self.image_width, self.image_height), color="white")
        self.draw = ImageDraw.Draw(self.image)

    def get_font(self, font_path, font_size):
        """
        Load a font from the given path with the specified size.
        """
        return ImageFont.truetype(font_path, font_size)

    def wrap_text_with_metadata(self, word_details):
        """
        Wrap text dynamically based on word details and organize into structured data.

        :param word_details: List of dictionaries containing word-specific details (font, size, color).
        :return: List of dictionaries, each representing a line with words and their metadata.
        """
        wrapped_lines = []
        current_line = []
        current_width = 0
        line_number = 1

        for details in word_details:
            word = details.get("word", "").strip()
            
            # If the word is an empty string, consider it a blank line
            if word == "":
                if current_line:  # Add the current line to wrapped lines before a blank line
                    wrapped_lines.append({
                        "line_number": line_number,
                        "words": current_line
                    })
                    current_line = []
                wrapped_lines.append({
                    "line_number": line_number,
                    "words": []  # Blank line
                })
                line_number += 1
                current_width = 0
                continue

            font = self.get_font(details["font_type"], details["font_size"])
            word_width = self.draw.textbbox((0, 0), word, font=font)[2]

            if current_width + word_width <= self.image_width - 40:  # Adjust margins
                details["line_number"] = line_number
                current_line.append(details)
                current_width += word_width + 10  # Add space between words
            else:
                wrapped_lines.append({
                    "line_number": line_number,
                    "words": current_line
                })
                current_line = [details]
                current_width = word_width + 10
                line_number += 1

        if current_line:  # Append the last line if any
            wrapped_lines.append({
                "line_number": line_number,
                "words": current_line
            })

        return wrapped_lines


# Example Usage
if __name__ == "__main__":
    # Image dimensions
    image_width = 1080
    image_height = 1080

    # Create an instance of DynamicTextWrapper
    dynamic_text = DynamicTextWrapper(image_width, image_height)

    # List of word details (input)
    word_details = [
        {"word": "This", "font_type": "arial.ttf", "font_size": 40, "color": "red"},
        {"word": "is", "font_type": "arial.ttf", "font_size": 30, "color": "blue"},
        {"word": "a", "font_type": "arial.ttf", "font_size": 35, "color": "green"},
        {"word": "", "font_type": "arial.ttf", "font_size": 35, "color": "green"},  # Blank line
        {"word": "dynamic", "font_type": "arial.ttf", "font_size": 50, "color": "purple"},
        {"word": "text", "font_type": "arial.ttf", "font_size": 45, "color": "orange"},
        {"word": "wrapping", "font_type": "arial.ttf", "font_size": 40, "color": "black"},
        {"word": "example.", "font_type": "/arial.ttf", "font_size": 38, "color": "brown"},
        {"word": "", "font_type": "arial.ttf", "font_size": 35, "color": "green"},  # Another blank line
        {"word": "New", "font_type": "arial.ttf", "font_size": 42, "color": "cyan"},
        {"word": "line", "font_type": "arial.ttf", "font_size": 42, "color": "cyan"}
    ]

    # Wrap text and structure it into metadata
    wrapped_lines = dynamic_text.wrap_text_with_metadata(word_details)

    # Print structured output
    for line in wrapped_lines:
        if not line["words"]:  # Blank line
            print(f"Line {line['line_number']}: [Blank Line]")
        else:
            print(f"Line {line['line_number']}:")
            for word in line["words"]:
                print(f"  Word: {word['word']}, Font: {word['font_type']}, "
                      f"Size: {word['font_size']}, Color: {word['color']}")
