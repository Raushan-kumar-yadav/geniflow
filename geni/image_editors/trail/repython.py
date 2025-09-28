import re

def analyze_and_format_text(text):
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
    text = re.sub(r'(?<=[!?])\s*(?=\S)', '\n\n', text)

    return text


# Example usage
input_text = (
    "Hello,world!This = is an example.It shows how to format text properly."
    "Another sentence follows here.  Here's another one without proper spaces!"
)

formatted_text = analyze_and_format_text(input_text)

print("Original Text:")
print(input_text)
print("\nFormatted Text:")
print(formatted_text)
