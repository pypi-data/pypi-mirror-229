import os
import sys
import keyboard
import colorama
colorama.init()
def ischar(char, error):
    if not len(char) == 1: raise error
def isansifore(obj, error):
    if not hasattr(colorama.Fore, obj): raise error
def isansiback(obj, error):
    if not hasattr(colorama.Back, obj): raise error
def isfunction(function):
    try:
        function()
        return True
    except TypeError:
        return False

class screen:
    def __init__(self, forecolor = "WHITE", backcolor = "BLACK", width = 32, height = 16, border: list = ["-", "|", "#", "#", "#", "#"], stdchar = " "):
        ischar(stdchar, SyntaxError("stdchar is not a single char"))
        isansifore(forecolor, SyntaxError(f"{forecolor} is not a valid attribute in colorama.ansi.ansiFore"))
        isansiback(backcolor, SyntaxError(f"{backcolor} is not a valid attribute in colorama.ansi.ansiBack"))
        index = 0
        for char in border:
            ischar(char, SyntaxError(f"border[{index}] is not a single char"))
            index += 1
        self.forecolor = getattr(colorama.Fore, forecolor)
        self.backcolor = getattr(colorama.Back, backcolor)
        self.width = width
        self.height = height
        self.stdchar = stdchar
        self.border = border
        self.values = []
        for i in range(self.height):
            for j in range(self.width):
                self.values.append(self.stdchar)
        self.colors = []
        for i in range(self.height):
            for j in range(self.width):
                self.colors.append(self.forecolor + self.backcolor)
    def update(self, clear = True):
        if clear: os.system("cls")
        render = ""
        render += self.border[2] + self.border[0] * self.width + self.border[3] + "\n"
        index = 0
        for i in range(self.height):
            render += self.border[1]
            for j in range(self.width):
                render += self.colors[index] + self.values[index]
                index += 1
            render += colorama.Fore.RESET + colorama.Back.RESET + self.border[1] + "\n"
        render += colorama.Fore.RESET + colorama.Back.RESET + self.border[4] + self.border[0] * self.width + self.border[5] + "\n"
        print(render)
    def fillChar(self, char):
        ischar(char, SyntaxError("char is not a single char"))
        self.values = []
        for i in range(self.height):
            for j in range(self.width):
                self.values.append(char)
    def fillColor(self, fore, back):
        isansifore(fore, SyntaxError(f"{fore} is not a valid attribute in colorama.ansi.ansiFore"))
        isansiback(back, SyntaxError(f"{back} is not a valid attribute in colorama.ansi.ansiBack"))
        self.colors = []
        for i in range(self.height):
            for j in range(self.width):
                self.colors.append(getattr(colorama.Fore, fore) + getattr(colorama.Back, back))
    def fill(self, char, fore, back):
        ischar(char, SyntaxError("char is not a single char"))
        isansifore(fore, SyntaxError(f"{fore} is not a valid attribute in colorama.ansi.ansiFore"))
        isansiback(back, SyntaxError(f"{back} is not a valid attribute in colorama.ansi.ansiBack"))
        self.values = []
        self.colors = []
        for i in range(self.height):
            for j in range(self.width):
                self.values.append(char)
                self.colors.append(getattr(colorama.Fore, fore) + getattr(colorama.Back, back))
    def coordsToIndex(self, x, y):
        index = 0
        for i in range(self.height):
            for j in range(self.width):
                if i == y and j == x:
                    return index
                index += 1
    def indexToCoords(self, index):
        for x in range(self.height):
            for y in range(self.width):
                if x * y == index:
                    return x, y
class setPixel:
    def byCoords(self, x: int, y: int, value: str):
        ischar(value, SyntaxError("value is not a single char"))
        index = 0
        for i in range(self.height):
            for j in range(self.width):
                if i == y and j == x:
                    self.values[index] = value
                index += 1
    def byIndex(self, index: int, value: str):
        self.values[index] = value
class getPixel:
    def byCoords(self, x: int, y: int):
        index = 0
        ret = 0
        for i in range(self.height):
            for j in range(self.width):
                if i == y and j == x:
                    ret = self.values[index]
                index += 1
        return ret
    def byIndex(self, index):
        return self.values[index]
class setPixelColor:
    def byCoords(self, x: int, y: int, fore, back):
        isansifore(fore, SyntaxError(f"{fore} is not a valid attribute in colorama.ansi.ansiFore"))
        isansiback(back, SyntaxError(f"{back} is not a valid attribute in colorama.ansi.ansiBack"))
        index = 0
        for i in range(self.height):
            for j in range(self.width):
                if i == y and j == x:
                    self.colors[index] = getattr(colorama.Fore, fore) + getattr(colorama.Back, back)
                index += 1
    def byIndex(self, index: int, fore, back):
        isansifore(fore, SyntaxError(f"{fore} is not a valid attribute in colorama.ansi.ansiFore"))
        isansiback(back, SyntaxError(f"{back} is not a valid attribute in colorama.ansi.ansiBack"))
        self.values[index] = getattr(colorama.Fore, fore) + getattr(colorama.Back, back)
class getPixelColor:
    def byCoords(self, x: int, y: int):
        index = 0
        ret = 0
        for i in range(self.height):
            for j in range(self.width):
                if i == y and j == x:
                    ret = self.colors[index]
                index += 1
        return ret
    def byIndex(self, index):
        return self.colors[index]
def mainLoop(loop):
    if not isfunction(loop): raise SyntaxError("loop is not a function")
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        os.system("cls")
        sys.exit(0)
class keys:
    def waitForKey(key1 = "none", key2 = "none", key3 = "none", key4 = "none", key5 = "none", key6 = "none"):
        press = 0
        while press == 0:
            try:
                keyboard.read_key()
            except KeyboardInterrupt:
                os.system("cls")
                sys.exit(0)
            if not key1 == "none":
                if keyboard.is_pressed(key1):
                    press = 1
            if not key2 == "none":
                if keyboard.is_pressed(key2):
                    press = 2
            if not key3 == "none":
                if keyboard.is_pressed(key3):
                    press = 3
            if not key4 == "none":
                if keyboard.is_pressed(key4):
                    press = 4
            if not key5 == "none":
                if keyboard.is_pressed(key5):
                    press = 5
            if not key6 == "none":
                if keyboard.is_pressed(key6):
                    press = 6
        return press
class sprite:
    def __init__(self, x, y, char, fore, back):
        ischar(char, SyntaxError("char is not a single char"))
        isansifore(fore, SyntaxError(f"{fore} is not a valid attribute in colorama.ansi.ansiFore"))
        isansiback(back, SyntaxError(f"{back} is not a valid attribute in colorama.ansi.ansiBack"))
        self.x = x
        self.y = y
        self.char = char
        self.hidden = True
        self.fore = fore
        self.back = back
    def update(self, screen):
        setPixel.byCoords(screen, self.x, self.y, self.char)
        setPixelColor.byCoords(screen, self.x, self.y, self.fore, self.back)
    def setChar(self, char):
        ischar(char, SyntaxError("char is not a single char"))
        self.char = char
    def setPos(self, x, y):
        self.x = x
        self.y = y
    def changePos(self, x, y):
        self.x += x
        self.y += y
    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y
    def changeX(self, x):
        self.x += x
    def changeY(self, y):
        self.y += y
    def setColor(self, fore, back):
        isansifore(fore, SyntaxError(f"{fore} is not a valid attribute in colorama.ansi.ansiFore"))
        isansiback(back, SyntaxError(f"{back} is not a valid attribute in colorama.ansi.ansiBack"))
        self.fore = fore
        self.back = back
class console:
    def clear():
        os.system("cls")
    def exit(code):
        sys.exit(code)
class text:
    def write(screen, text: str, x, y, fore, back):
        chars = 0
        currx = x
        curry = y
        for char in text:
            if char == "\n":
                curry += 1
                currx -= chars
                chars = 0
                continue
            setPixel.byCoords(screen, currx, curry, char)
            setPixelColor.byCoords(screen, currx, curry, fore, back)
            currx += 1
            chars += 1