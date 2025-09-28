from PIL import Image, ImageDraw, ImageFont
import pandas as pd


class Creat_image:
    """
    This class creates text on an image with different fonts and font sizes.
    """

    def __init__(self, BgImage, BoldFont, RegularFont, FontSize):
        self.BgImage = BgImage
        self.draw = ImageDraw.Draw(self.BgImage)
        self.BoldFont = BoldFont
        self.RegularFont = RegularFont
        self.fontSize = FontSize
        self.ImageWidth, self.ImageHeight = self.BgImage.size

        print(self.ImageWidth, self.ImageHeight)

    def ProcessExcelPara(self, filepath):
        df = pd.read_excel(filepath)
        Text_cell = str(df.iloc[2, 0])  # Get the first cell's content as a string

        left_margin = 100
        right_margin = 80
        max_width = self.ImageWidth - left_margin - right_margin  # Account for margins

        # Load the bold font
        bold_font = ImageFont.truetype(self.BoldFont, self.fontSize)

        # Calculate line height
        line_height = self.draw.textbbox((0, 0), "A", font=bold_font)[3] + 5

        # Wrap the text
        lines = []
        paragraphs = Text_cell.split("\n")  # Split text into paragraphs by blank lines

        for paragraph in paragraphs:
            if paragraph.strip():  # If the line is not blank
                words = paragraph.split()
                current_line = []
                for word in words:
                    test_line = " ".join(current_line + [word])
                    print(test_line)
                    text_width = self.draw.textbbox((0, 0), test_line, font=bold_font)[2]
                    print(text_width)
                    if text_width <= max_width:  # Check if the line fits within the available width
                        current_line.append(word)
                    else:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(" ".join(current_line))
            else:
                lines.append("")  # Add a blank line for empty paragraphs

        return lines

    def addingTextAndPara(self, textlist, fontsize=50):

        bold_font_size = fontsize
        regular_font_size = fontsize - 20
        lines = []

        Number_of_element_in_textlist = len(textlist)
        print(Number_of_element_in_textlist)

        fontsize_list = [regular_font_size] * Number_of_element_in_textlist
        if Number_of_element_in_textlist <= 3:
            fontsize_list[0] = bold_font_size
            fontsize_list[-1] = regular_font_size 
        else:
            fontsize_list[0] = bold_font_size
            fontsize_list[-1] = regular_font_size

        fontpaths_list = [self.RegularFont] * Number_of_element_in_textlist

        if Number_of_element_in_textlist <= 3:
            fontpaths_list[0] = self.BoldFont
            fontpaths_list[-1] = self.RegularFont
        else:
            fontpaths_list[0] = self.BoldFont
            fontpaths_list[-1] = self.BoldFont

        for text, fontsz, fontpt in zip(textlist, fontsize_list, fontpaths_list):
            line_dict = {
                "text": text,
                "font_size": fontsz,
                "font_path": fontpt
            }
            lines.append(line_dict)

        return lines

    def DrawText(self, lines):
        total_line_height = 0

        # Calculate total height of text
        for line in lines:
            font = ImageFont.truetype(line["font_path"], line["font_size"])
            _, _, _, h = self.draw.textbbox((0, 0), line["text"], font=font)
            total_line_height += h

        print(total_line_height)

        # Starting Y-coordinate for text
        y = (self.ImageHeight - total_line_height) / 2

        # Loop through each line
        for line in lines:
            font = ImageFont.truetype(line["font_path"], line["font_size"])
            _, _, w, h = self.draw.textbbox((0, 0), line["text"], font=font)

            # Draw the text
            self.draw.text((100, y), line["text"], font=font, fill="black")

            # Update Y-coordinate for the next line
            y += h + 10  # Add some spacing between lines

        # Save or display the image
        self.BgImage.show()  # Display the image
        self.BgImage.save("output.png")  # Save the image


# Create a blank image
image = Image.new('RGB', (1080, 1080), color='white')

# Initialize the class with required parameters
mytest = Creat_image(
    BgImage=image,
    BoldFont="fonts\San-Francisco\San Francisco\pro\SF-Pro-Display-Bold.otf",
    RegularFont="fonts\San-Francisco\San Francisco\pro\SF-Pro-Text-Regular.otf",
    FontSize=50
)

# Process text from Excel and add it to the image
excel_text_lines = mytest.ProcessExcelPara("csv/Book1.xlsx")
formatted_text_lines = mytest.addingTextAndPara(excel_text_lines)
mytest.DrawText(formatted_text_lines)
