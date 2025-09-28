from PIL import Image, ImageDraw, ImageFont
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('vader_lexicon')

class AdvancedTextImageFormatter:
    def __init__(self, font_path="arial.ttf", font_size=50, image_size=(800, 600), output_path="output.png", fill="black"):
        self.font_path = font_path
        self.font_size = font_size
        self.image_size = image_size
        self.output_path = output_path
        self.fill = fill
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.image = Image.new("RGB", self.image_size, "white")
        self.draw = ImageDraw.Draw(self.image)

    def analyze_and_structure_text(self, text):
        """
        Analyzes the input text and structures it by adding spaces and blank lines based on emotions and meaning.

        Args:
            text (str): Input text.

        Returns:
            str: Structured text with meaningful formatting.
        """
        # Tokenize text into sentences
        sentences = sent_tokenize(text)

        # Initialize sentiment analyzer
        sia = SentimentIntensityAnalyzer()

        formatted_sentences = []
        previous_emotion = None

        for sentence in sentences:
            # Analyze the sentiment of the sentence
            sentiment = sia.polarity_scores(sentence)
            emotion = "neutral"
            if sentiment["compound"] > 0.2:
                emotion = "positive"
            elif sentiment["compound"] < -0.2:
                emotion = "negative"

            # Add a blank line if emotion changes
            if previous_emotion and previous_emotion != emotion:
                formatted_sentences.append("")  # Add blank line

            formatted_sentences.append(sentence.strip())  # Add the sentence
            previous_emotion = emotion

        return formatted_sentences

    def split_text_to_fit_width(self, text):
        """
        Splits a given paragraph into lines that fit within the image width.

        Args:
            text (str): Input paragraph.

        Returns:
            list: List of strings where each string fits within the image width.
        """
        max_width = self.image_size[0] - 40  # Leave some padding
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            # Test the line width with the next word
            test_line = f"{current_line} {word}".strip()
            line_width = self.draw.textlength(test_line, font=self.font)

            if line_width > max_width:  # If adding the word exceeds max width
                lines.append(current_line.strip())
                current_line = word  # Start a new line
            else:
                current_line = test_line

        if current_line:  # Add the last line
            lines.append(current_line.strip())

        return lines

    def create_image_with_text(self, text):
        """
        Creates an image with the formatted text centered and structured.

        Args:
            text (str): Input text to format and fit in the image.
        """
        structured_text = self.analyze_and_structure_text(text)
        y_position = 20  # Start drawing from the top, with some padding

        for paragraph in structured_text:
            if paragraph == "":  # Blank line for spacing
                y_position += self.font_size
            else:
                # Split paragraph into lines to fit within the image width
                lines = self.split_text_to_fit_width(paragraph)

                for line in lines:
                    # Center each line horizontally
                    line_width = self.draw.textlength(line, font=self.font)
                    x_position = (self.image_size[0] - line_width) // 2
                    self.draw.text((x_position, y_position), line, fill=self.fill, font=self.font)
                    y_position += self.font_size  # Move to the next line

                y_position += self.font_size // 2  # Add some extra space between paragraphs

        # Save and show the final image
        self.image.save(self.output_path)
        self.image.show()

# Example Usage
input_text = (
    "I had a wonderful day. The weather was amazing, and I felt so alive. "
    "But then, something terrible happened. I lost my wallet, and I felt awful. "
    "Thankfully, someone returned it to me. There are still good people in this world."
)

# Initialize formatter
formatter = AdvancedTextImageFormatter(
    font_path="arial.ttf",  # Provide a valid .ttf font file path
    font_size=40,
    image_size=(800, 600),
    output_path="formatted_text_image.png",
    fill="black"
)

# Generate the image with formatted text
formatter.create_image_with_text(input_text)
