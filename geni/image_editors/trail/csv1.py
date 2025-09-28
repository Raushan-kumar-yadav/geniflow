import pandas as pd
from PIL import Image, ImageDraw, ImageFont



def PrecessExcelPara(filelpath):
        
    df = pd.read_excel(filelpath)
    Text_cell = df.iloc[0,0]  # Get the first cell's content

    lines = []
    # Ensure cell is a string and split by newlines if present
    if isinstance(Text_cell, str):
        for line in Text_cell.splitlines():
            lines.append(line)  # Split each line into words
    else:
        print("The input is not a string")
    return lines



test2 = PrecessExcelPara("csv\Book1.xlsx")
print(test2)
