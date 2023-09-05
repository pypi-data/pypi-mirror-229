import all as wingsys
window = wingsys.screen("BLACK", "GREEN", 64, 32, ["═", "║", "╔", "╗", "╚", "╝"], " ")
test = wingsys.sprite(0, 0, "●", "RED", "BLACK")

def loop():
    window.fill(" ", "BLACK", "GREEN")
    wingsys.text.write(window, "● Yo\n● Yo []\n● hello\n● yo friend\n●\n●\n●\n●\n●\n●\n●\n●\n●\n●\n●", 0, 0, "GREEN", "BLACK")
    test.update(window)
    window.update()
    print(f"x{test.x} y{test.y}")
    key = wingsys.keys.waitForKey("up", "down", "left", "right", "esc")
    if key == 1:
        test.changeY(-1)
    if key == 2:
        test.changeY(1)
    #if key == 3:
    #    test.changeX(-1)
    #if key == 4:
    #    test.changeX(1)
    if key == 5:
        wingsys.console.clear()
        wingsys.console.exit(0)
wingsys.mainLoop(loop)