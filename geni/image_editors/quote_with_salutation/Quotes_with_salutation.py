from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import random


class Creat_image:
    """
    This class creates text on an image with different fonts and font sizes.
    """

    def __init__(self, BgImage, BoldFont, RegularFont, FontSize,firstList = [],secondList = []):

        self.firstList = firstList
        self.secondList = secondList
        self.BgImage = BgImage
        self.draw = ImageDraw.Draw(self.BgImage)
        self.BoldFont = BoldFont
        self.RegularFont = RegularFont
        self.fontSize = FontSize
        self.ImageWidth, self.ImageHeight = self.BgImage.size

        print(self.ImageWidth, self.ImageHeight)

    def ProcessExcelPara(self, filepath):
        df = pd.read_excel(filepath)
        Text_cell = str(df.iloc[4, 0])  # Get the first cell's content as a string

        left_margin = 100
        right_margin = 80
        max_width = self.ImageWidth - left_margin - right_margin  # Account for margins

        # Load the bold font
        regular_font = ImageFont.truetype(self.RegularFont, self.fontSize)

        # Calculate line height
        line_height = self.draw.textbbox((0, 0), "A", font=regular_font)[3] + 5

        # Wrap the text
        lines = []
        paragraphs = Text_cell.split("\n")  # Split text into paragraphs by blank lines
        print("this is paragtaph",paragraphs)

        for paragraph in paragraphs:
            if paragraph.strip():  # If the line is not blank
                words = paragraph.split()
                current_line = []
                for word in words:
                    test_line = " ".join(current_line + [word])
                    text_width = self.draw.textbbox((0, 0), test_line, font=regular_font)[2]
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
    

    def txttolist(self,file_path):
        with open(file_path, "r") as file:
            # Read all lines from the file
            lines = file.readlines()

        # Initialize an empty list to store content between blank lines
        result = []

        # Temporary variable to hold content between blank lines
        current_content = []

        # Loop through each line
        for line in lines:
            # Strip any leading/trailing whitespaces from the line
            stripped_line = line.strip()

            # If the line is blank, we consider it a separator between content blocks
            if stripped_line == "":
                if current_content:
                    result.append(" ".join(current_content))  # Add the content between blank lines as a string
                    current_content = []  # Reset for the next block
            else:
                current_content.append(stripped_line)  # Collect content between blank lines

        # Add the last content if any remains (after the final blank line or end of file)
        if current_content:
            result.append(" ".join(current_content))

        return result



    
    def addingsalutation(self,textlist,salutationLIstPath="",lastsalutatinListPath=""):

        salutationLIst = self.txttolist(salutationLIstPath)
        lastsalutatinList = self.txttolist(lastsalutatinListPath)

        salutation = str(random.choice(salutationLIst))
        lastsalutatin = str(random.choice(lastsalutatinList))
        current_line = textlist
        
        #hard cordig salutation and last saluatation

        current_line.insert(0,salutation)
        current_line.insert(1," ")
        current_line.insert(2,"")
        current_line.append(" ")
        current_line.append("")
        current_line.append(lastsalutatin)

        return current_line




    def addingTextAndPara(self, textlist):
        lines = []

        Number_of_element_in_textlist = len(textlist)
        print(Number_of_element_in_textlist)

        fontsize_list = [self.fontSize] * Number_of_element_in_textlist
        if Number_of_element_in_textlist <= 3:
            fontsize_list[0] = self.fontSize + 15
            fontsize_list[-1] = self.fontSize
        else:
            fontsize_list[0] = self.fontSize + 15
            fontsize_list[-1] = self.fontSize - 10

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
    FontSize=40
)

# Process text from Excel and add it to the image
excel_text_lines = mytest.ProcessExcelPara("csv/Book1.xlsx")
print("this is before assign into text font and color",excel_text_lines)
aftersal = mytest.addingsalutation(excel_text_lines,"quote_with_salutation\salutatin.txt","quote_with_salutation\lastsal.txt")
formatted_text_lines = mytest.addingTextAndPara(aftersal)
print(formatted_text_lines)
mytest.DrawText(formatted_text_lines)
