from PIL import imagedraw , Image , ImageFont
import pandas as pd 

class textplacing():

    def __init__(self,text,textcolor,boldfont,regularfont,bgcolor,bghight,bgwidth,fontSize):

        self.text = text
        self.textcolor = textcolor
        self.boldfont = boldfont 
        self.fontSize = fontSize
        self.regularfont = regularfont
        self.bgcolor = bgcolor
        self.bghight = bghight
        self.bgwidth = bgwidth
        self.drawimge = Image.new('RGB',(self.bghight,self.bgwidth),color=bgcolor)
        self.draw = imagedraw.Draw(self.drawimge)


        
