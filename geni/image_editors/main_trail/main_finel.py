from ctypes import alignment
from email.mime import image
from ftplib import error_perm
from opcode import opname
from os import replace
from webbrowser import open_new
from PIL import Image, ImageDraw, ImageFont
from networkx import center
import pandas as pd
import random
import time 
from regex import F
from QuoteScrapper.QuoteScapper import QuoteScraper # This is the class that we are going to use to scrape quotes from the web
import re
from ollama_me.llama_me import LlamaChat
from PinterestImageScrapper.PinterestDownloader import PinterestImageScrapper
from Object_decatation.Detection import ImageDetection


class QuotesMaker():

    def __init__(self, BgImage, BoldFontPath='arialbd.ttf', RegularFontPath='arial.ttf', FontSize=40,salutationList = [],SignOffList = [],logoImagePath = '',FontFill='black',FontHighlightcolor='yellow',logoSize=(100,100),OutputPath='output.png',ImageSize=(1080,1080),LeftMargin=100,RightMargin=80,default_font="fonts\San-Francisco\San Francisco\otf\SFNSDisplay-Black.otf"):

        self.Bgimage = BgImage
        self.BoldFontPath = BoldFontPath
        self.RegularFontPath = RegularFontPath
        self.FontSize=FontSize
        self.salutationList = salutationList
        self.signOffList = SignOffList
        self.logoImagePath = logoImagePath
        self.FontFill = FontFill
        self.fonthighlightcolor = FontHighlightcolor
        self.logoSize = logoSize
        self.OutputPath = OutputPath
        self.ImageSize = ImageSize
        self.LeftMargin = LeftMargin
        self.RightMargin = RightMargin
        self.default_font = default_font

    
    def WhereTOgetQuote(self,fromWhere='',filepath='',url='',element_selector=''):

        """ This function is going to be used to get the quote from the source that the user has provided """

        """
          Args:
         
            fromWhere (str): The source from where the quote is going to be fetched. It can be 'excel', 'web', 'ChatBot'
            
        """

        """ Returns:
            str: THE quote that is fateched form the source that the user has provided"""


        if fromWhere == 'excel':
            df = pd.read_excel(filepath)
            Text_cell = str(df.iloc[0,0]) 
            
            return Text_cell
        elif fromWhere == 'web':
            
            scrapper = QuoteScraper(url,element_selector) # This is the object of the QuoteScraper class
            scraped_quote = scrapper.scrape_text_from_website() # This is the method that we are going to use to scrape the quote from the web
            return scraped_quote
        elif fromWhere == 'ChatBot':
            pass
        else:
            print('Please provide a valid source')
            return None
        
    
    def progress_paragraph(self, paragraph):
        pass

    def adding_blank_line(self, text):
    
        """
        Analyzes a given text to add spaces after punctuation
        and blank lines between sentences where necessary.

        Args:
            text (str): The input text to analyze and format.

        Returns:
            str: The formatted text.
        """
        # Add a space after punctuation if missing
        text = re.sub(r'([.,;!?])(?=\S)', r'\1 ', text)

        # Add a blank line after a sentence ending with a period
        text = re.sub(r'(?<=[!?:])\s*(?=\S)', '\n\n', text)

        return text
    
    def AskformAI(self,text): #we have to improve this function later
        """
        This function is going to be used to ask the AI to detect the emotion in the text that the user has provided
        :param text: The input text to analyze.
        :return: Sorted emotions with confidence scores.
        
        """
        # Initialize the pipeline

        results = LlamaChat().chat(text=text)


        # Check if results is None
        if results is None:
            print("No results returned.")
            return []
        

       # Split the string into lines
        lines = results.strip().split("\n")

        print(lines)

        # Initialize an empty list to store the extracted descriptions
        Filtered_lists = lines[-3:]
        results_list = []

        for element in Filtered_lists:
            em = element.replace("1","").replace("2","").replace("3","").replace(".","").replace("**","")
            
            results_list.append(em)


        # Iterate through the lines to find lines after numbered suggestions
        


        return results_list
    
    def RandomSelector(self,list):

        """
        This function is going to be used to select a random element from the given list 

        Args:list

        return: str: The random element that is selected from the list
        """
        
        return random.choice(list)
    
    def pintrest_image_downloader (self,text,user_data_dir,profile_dir,excelpath):
        
        """
        This function is going to download image form pintrest 

        Args: text

        return :
        image
        
        """

        chrome_profile = PinterestImageScrapper(user_data_dir, profile_dir, excelpath)
        chrome_profile.force_quit_all_chrome()
        chrome_profile.start_browser()
        time.sleep(3)
        chrome_profile.search(query=text)
        time.sleep(5)
        imageLink = chrome_profile.get_link()
        if imageLink:
            print("this is image link" + imageLink[0])
            saved_image_path = chrome_profile.image_save(imageURL=imageLink)
        else:
            print("No image links found.")
        time.sleep(5)
        chrome_profile.close_browser()

        return saved_image_path
    
    
    def image_anyliser(self,Image_Path,Model_path):
        
        detector = ImageDetection(image_path=Image_Path,model_path=Model_path)
        image_data = detector.image_detection()

        return image_data
    


    def RandomAlignment(self):
        """
        this method return random alognment 
        Args: nothing 

        Return : return random aligment
        
        
        """


        alignment = ["centered","top","right","bottom","left"]

        return random.choice(alignment)


    def create_font_dictionary(self,paragraph,font ='arial.ttf',font_size = 25 , font_color = 'black'):
        """Create a dictionary where each word occurrence is tracked with unique attributes."""
        words = paragraph.split()
        font_styles = font
        font_sizes = font_size
        font_colors = font_color

        word_dict = {}
        for idx, word in enumerate(words):
            # Add a unique key for each word occurrence using its position
            key = f"{word}_{idx}"
            word_dict[key] = {
                'font_path': font_styles,
                'font_size': font_sizes,
                'font_color': font_colors
            }
        return word_dict


    
    

    

    def calculate_text_block(self,text_config, line_spacing=1.2):
        """
        Calculate wrapped lines and text block height with font-aware metrics.

        Args:
            text_config (dict): {word: {'font_size': int, 'font_path': str}}
            max_width (int): Maximum line width in pixels
            line_spacing (float): Multiplier for line height (default: 1.2)

        Returns:
            dict: {
                'wrapped_lines': list of wrapped text lines,
                'line_count': int,
                'max_font_size': int,
                'block_height': float
            }
        """
        lines, current_line = [], []
        line_count = 0
        current_width = 0
        max_font_size = 0
        current_line_max_font = 0
        img = Image.open(r"downloaded_image.jpg")
        image_weidth,image_height = img.size
        max_width = image_weidth - 100

        for full_word in text_config:
            # Process word and get font config
            display_word = full_word.split('_')[0]
            config = text_config[full_word]
            font_size = config['font_size']

            # Update font size tracking
            current_line_max_font = max(current_line_max_font, font_size)
            max_font_size = max(max_font_size, font_size)

            # Load font and calculate metrics
            try:
                font = ImageFont.truetype(config['font_path'], font_size)
            except:
                print("not able to locate font_path using defalult font")
                font = ImageFont.load_default()

            
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), display_word, font=font)
            word_width = bbox[2] - bbox[0]
            space_width = draw.textbbox((0, 0), " ", font=font)[2]

            # Calculate effective width (word + space)
            effective_width = word_width + (space_width if current_line else 0)

            # Wrap logic
            if current_width + effective_width > max_width:
                lines.append(" ".join(current_line))
                line_count += 1
                current_line = [display_word]
                current_width = word_width
                current_line_max_font = font_size
            else:
                if current_line:
                    current_width += space_width
                current_line.append(display_word)
                current_width += word_width

        # Add final line
        if current_line:
            lines.append(" ".join(current_line))
            line_count += 1

        # Calculate block height
        block_height = line_count * max_font_size * line_spacing

        return (max_width,block_height)
        

    def calculate_text_block_with_first_line_bold(self, text_config, line_spacing=1.2):
        """
        Updates text_config dictionary with line-specific font modifications.
        - First line uses bold font.
        - Subsequent lines retain their original fonts.
        - Returns updated dictionary with adjusted font paths.
        """
        updated_config = {}  # Store modified configurations
        lines, current_line = [], []
        line_count = 0
        current_width = 0
        max_font_size = 0
        current_line_index = 0  # Track which line we're on

        # Ensure every word has 'font_path' and 'font_size'
        for word, config in text_config.items():
            if "font_path" not in config:
                config['font_path'] = self.default_font
            if "font_size" not in config:
                config['font_size'] = 20  # Default size

        # Create a blank image for text measurements
        img = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(img)

        # Get image width
        with Image.open(r"downloaded_image.jpg") as img_ref:
            image_width, _ = img_ref.size
            max_width = image_width - 100

        for full_word in text_config:
            # Process word and copy its configuration
            display_word = full_word.split('_')[0]
            config = text_config[full_word].copy()  # Preserve original config

            # Override font path for the first line
            if current_line_index == 0:
                config['font_path'] = self.BoldFontPath

            # Load font safely
            font_path = config.get('font_path', self.default_font)  # Fix KeyError
            font_size = config.get('font_size', 20)  # Ensure size is set

            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.truetype(self.default_font, font_size)

            # Measure word width
            bbox = draw.textbbox((0, 0), display_word, font=font)
            word_width = bbox[2] - bbox[0]

            # Measure space width safely
            space_bbox = draw.textbbox((0, 0), " ", font=font)
            space_width = space_bbox[2] - space_bbox[0]

            # Track max font size for spacing
            max_font_size = max(max_font_size, font_size)

            # Line wrapping logic
            effective_width = word_width + (space_width if current_line else 0)
            if current_width + effective_width > max_width:
                lines.append(" ".join(current_line))
                line_count += 1
                current_line = [display_word]
                current_width = word_width
                current_line_index += 1  # Move to next line
            else:
                if current_line:
                    current_width += space_width
                current_line.append(display_word)
                current_width += word_width

            # Store updated configuration
            updated_config[full_word] = config
        block_height = line_count * max_font_size * line_spacing
        # Ensure last line is added
        if current_line:
            lines.append(" ".join(current_line))
            line_count += 1

        return [updated_config,(max_width,block_height)] # Return modified dictionary


    def AskAlignment(self, alignment,ImagePath, text_block_size=(100, 50)): #Improve this method furture
        """
        Calculates the position based on the alignment preference.

        Args:
            alignment (str): Alignment preference ("centered", "left", "right", "top", "bottom").
            text_block_size (tuple): Width and height of the text block.

        Returns:
            tuple: The (x, y) coordinates for the text.
        """
        img = Image.open(ImagePath)
        text_width, text_height = text_block_size
        image_width, image_height = img.size

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

        return (x, y)
    

    def CalculatePosition(self, image_path, coordinate, text_block_size=(100, 50)):
        """
        This function calculates the position of text based on coordinates provided by YOLO.

        Args:
            image_path (str): Path to the image.
            coordinate (list): List containing a dictionary with 'Coordinates'.
                               Example: [{'Coordinates': (x_start, y_start, width, height)}]
            label (str, optional): Optional label for the text.
            text_block_size (tuple): Dimensions of the text block (width, height).

        Returns:
            tuple: (x, y) position for the text.
        """
        # Open the image and get dimensions
        img = Image.open(image_path)
        image_width, image_height = img.size
        
        # Extract YOLO coordinates
        coordinate_start, coordinate_end, coordinate_width, coordinate_height = coordinate[0]["coordinates"]
        
        # Calculate centers
        image_vertical_center = image_height // 2
        image_horizontal_center = image_width // 2
        text_width, text_height = text_block_size

        # Determine text position
        if coordinate_start <= image_vertical_center:
            if coordinate_end <= image_horizontal_center:
                # Top-left placement
                x = 50  # Padding from the left
                y = 50  # Padding from the top
            elif coordinate_end > image_horizontal_center:
                # Top-right placement
                x = image_width - text_width - 50
                y = 50
            else:
                # Centered at the top
                x = (image_width - text_width) // 2
                y = 50
        elif coordinate_start > image_vertical_center:
            if coordinate_end <= image_horizontal_center:
                # Bottom-left placement
                x = 50
                y = image_height - text_height - 50
            elif coordinate_end > image_horizontal_center:
                # Bottom-right placement
                x = image_width - text_width - 50
                y = image_height - text_height - 50
            else:
                # Centered at the bottom
                x = (image_width - text_width) // 2
                y = image_height - text_height - 50

        # Centered in the middle
        if coordinate_start == image_vertical_center:
            x = (image_width - text_width) // 2
            y = (image_height - text_height) // 2
        
        return x, y

    def generate_random_color(self):
        """Generate a random color in hexadecimal format."""
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))


    def draw_wrapped_text(self, image_path, text_config, block_dimensions, aligment):
        """
        Draws text on an image using the wrapped text configuration.
        - Uses specified font, size, and color for each word.
        - Positions text according to block height and width.
        """
        # Load image
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        max_width, _ = block_dimensions  # Get text block width

        # Start drawing position
        x, y = aligment
        start_x, start_y = aligment
        max_font_size = 0  # Track the max font size per line
        current_width = 0
        current_line = []

        for full_word in text_config:
            display_word = full_word.split('_')[0]
            config = text_config[full_word]

            # Load font properties
            font_path = config.get('font_path', self.default_font)
            font_size = config.get('font_size', 20)
            font_color = config.get('font_color', (0, 0, 0))  # Default black

            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.truetype(self.default_font, font_size)

            # Measure word width
            bbox = draw.textbbox((0, 0), display_word, font=font)
            word_width = bbox[2] - bbox[0]

            # Measure space width
            space_bbox = draw.textbbox((0, 0), " ", font=font)
            space_width = space_bbox[2] - space_bbox[0]

            # Word wrapping check
            effective_width = word_width + (space_width if current_line else 0)
            if current_width + effective_width > max_width:
                # Move to next line
                y += max_font_size * 1.2  # Apply line spacing
                x = start_x
                current_width = 0
                max_font_size = 0
                current_line = []

            # Draw text
            draw.text((x, y), display_word, font=font, fill=font_color,align="center")
            x += word_width + space_width  # Move cursor forward
            current_width += word_width + space_width
            max_font_size = max(max_font_size, font_size)  # Update max font size

        # Save image
        img.show()
        
        










    


        













    




#try:
if __name__ == "__main__":

    
    text = "Success doesn’t come from what you do occasionally; it comes from what you do consistently. Keep pushing, keep growing, and greatness will follow."
    qt = QuotesMaker('bg.jpg',salutationList = ['Mr','Mrs','Dr'],SignOffList = ['Yours Truly','Sincerely'],logoImagePath = 'logo.png',OutputPath='output2.png')
    qt2 = qt.WhereTOgetQuote(filepath='csv\Book1.xlsx',fromWhere='excel',url='https://www.shopify.com/blog/motivational-quotes',element_selector='body > div:nth-child(2) > main:nth-child(2) > section:nth-child(2) > article:nth-child(2) > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > ol:nth-child(12) > li:nth-child(2)')
    qt3 = qt.adding_blank_line(qt2)
    q4 = qt.AskformAI(qt2)
    q5 = qt.RandomSelector(list=q4)
    #q6 = qt.pintrest_image_downloader(text=q5,user_data_dir=r"C:/Users/raush/AppData/Local/Google/Chrome/User Data",profile_dir="profile 7",excelpath=r"csv\used_image_from_pin.xlsx")
    q7 = qt.image_anyliser(Image_Path=r"downloaded_image.jpg",Model_path="yolo11n.pt")
    q8 = qt.CalculatePosition(image_path=r"downloaded_image.jpg",coordinate=q7)
    q9 = qt.create_font_dictionary(qt2)
    q10 = qt.calculate_text_block(q9)
    q11 = qt.calculate_text_block_with_first_line_bold(q9)
    text_config = q11[0]
    block_dim = q11[1]
    q_alig = qt.AskAlignment("bottom",r"downloaded_image.jpg",text_block_size=block_dim)
    q12 = qt.draw_wrapped_text(r"downloaded_image.jpg",text_config=text_config,block_dimensions=block_dim,aligment=q_alig)
    print("this is created font dic",q9)
    print("this is wrapped text and number of line ",q10)
    print("this is frist line bold wrapped =",q11)

    print(q4)
    print(qt3)
    
    print(q7)
    print("ths is calculated position for text placing ",q8)