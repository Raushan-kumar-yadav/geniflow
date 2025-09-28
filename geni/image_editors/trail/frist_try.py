def create_font_dictionary(paragraph,font = 'arial.ttf',font_size = 25 , font_color = 'black'):
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



df = create_font_dictionary("hello world")
print(df)