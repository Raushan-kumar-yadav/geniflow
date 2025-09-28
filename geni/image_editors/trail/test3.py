from PIL import Image, ImageDraw, ImageFont


class Creat_image:
    """
    This class is going to create text on an image with different font and font size
    """

    def __init__(self, BgImage, text, BoldFont, RegularFont, FontSize):
        self.BgImage = BgImage
        self.draw = ImageDraw.Draw(self.BgImage)
        self.text = text
        self.BoldFont = BoldFont
        self.RegularFont = RegularFont
        self.fontSize = FontSize
        self.ImageWidth, self.ImageHeight = self.BgImage.size

        print(self.ImageWidth, self.ImageHeight)

    def ProgressParagraph(self, paragraph='test2.txt'):
        try:
            with open(paragraph, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            # Remove any trailing newline characters
            return [line.rstrip() for line in lines]
        except FileNotFoundError:
            print(f"Error: The file at '{paragraph}' was not found.")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def addingTextAndPara(self, textlist=[], fontsize=40, Boldfontpath="fonts\\San-Francisco\\San Francisco\\pro\\SF-Pro-Display-Bold.otf", Regularfontpath="fonts\\San-Francisco\\San Francisco\\pro\\SF-Pro-Text-Regular.otf"):
        lines = []
        Number_of_elements_in_textlist = len(textlist)
        print(Number_of_elements_in_textlist)

        fontsize_list = [fontsize] * Number_of_elements_in_textlist
        if Number_of_elements_in_textlist <= 3:
            fontsize_list[0] = fontsize + 20
            fontsize_list[-1] = fontsize
        else:
            fontsize_list[0] = fontsize + 20
            fontsize_list[-1] = fontsize - 10

        fontpaths_list = [Regularfontpath] * Number_of_elements_in_textlist

        if Number_of_elements_in_textlist <= 3:
            fontpaths_list[0] = Boldfontpath
            fontpaths_list[-1] = Regularfontpath
        else:
            fontpaths_list[0] = Boldfontpath
            fontpaths_list[-1] = Boldfontpath

        for text, fontsz, fontpt in zip(textlist, fontsize_list, fontpaths_list):
            line_dict = {
                "text": text,
                "font_size": fontsz,
                "font_path": fontpt
            }
            lines.append(line_dict)

        return lines

    def DrawText(self, lines):
        # Define lines of text with their font size and style
        total_line_height = 0

        for line in lines:
            font = ImageFont.truetype(line["font_path"], line["font_size"])
            _, _, w, h = self.draw.textbbox((0, 0), line["text"], font=font)
            total_line_height += h

        print(total_line_height)
        # Starting Y-coordinate for text
        y = (self.ImageHeight - total_line_height) / 2

        # Loop through each line
        for line in lines:
            # Load the font with specified size
            font = ImageFont.truetype(line["font_path"], line["font_size"])

            # Get text size for positioning
            _, _, w, h = self.draw.textbbox((0, 0), line["text"], font=font)

            # Draw the text
            self.draw.text((100, y), line["text"], font=font, fill="black")

            # Update Y-coordinate for the next line
            y += h + 10  # Add some spacing between lines

        # Save or display the image
        self.BgImage.show()  # Display the image
        self.BgImage.save("output4.png")  # Save the image


image = Image.new('RGB', (1080, 1080), color='white',)
image_width, image_height = image.size
print(image_width, image_height)

mytest = Creat_image(BgImage=image, text='test2.txt', BoldFont=None, RegularFont=None, FontSize=None)
mytest1 = mytest.ProgressParagraph(paragraph='test2.txt')
print(mytest1)

mytest2 = mytest.addingTextAndPara(mytest1)

final = mytest.DrawText(mytest2)
