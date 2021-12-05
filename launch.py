"""
Wait for button presses and log events.
"""

from lpminimk3 import ButtonEvent, Mode, find_launchpads, colors
from lpminimk3.region import Labeled
import random
import time
import sys
import numpy as np
import random



class GameOfLifeSeq():
    COLS = 8
    ROWS = 8
    started = False
    def __init__(self):
        self.currentCol = 0
        self.pattern = self.getPattern(self.ROWS,self.COLS)
        self.oldpattern = self.getPattern(self.ROWS,self.COLS)
        self.lp = find_launchpads()[0]  # Get the first available launchpad
        self.lp.open()  # Open device for reading and writing on MIDI interface (by default)  # noqa

        self.lp.mode = Mode.PROG  # Switch to the programmer mode

    @staticmethod
    def update(cur):
        nxt = np.zeros((cur.shape[0], cur.shape[1]))

        for r, c in np.ndindex(cur.shape):
            num_alive = np.sum(cur[r-1 if r != 0 else 0:r+2, c-1 if c != 0 else 0:c+2]) - cur[r, c]

            col = 0
            if (cur[r, c] == 1 and 2 <= num_alive <= 3) or (cur[r, c] == 0 and num_alive == 3):
                nxt[r, c] = 1
                col = 1

            col = col if cur[r, c] == 1 else 0

        return nxt

    @staticmethod
    def getPattern(rows, columns):
        return np.array([(0, 0, 1, 0, 0, 1, 0, 0),
                         (0, 0, 1, 0, 0, 1, 0, 0),
                         (1, 1, 0, 1, 1, 0, 1, 1),
                         (0, 0, 1, 0, 0, 1, 0, 0),
                         (0, 0, 1, 0, 0, 1, 0, 0),
                         (1, 1, 0, 1, 1, 0, 1, 1),
                         (0, 0, 1, 0, 0, 1, 0, 0),
                         (0, 0, 1, 0, 0, 1, 0, 0)])
        X= np.zeros((rows, columns))

        blinker = [1, 1, 1]
        toad = [[1, 1, 1, 0],[0, 1, 1, 1]]
        X[2, 5:9] = blinker
        X[2:4, 2:6] = toad
        return X

        #tempArray = []
        #for row in range(rows):
        #    tempArray.append([])
        #    for col in range(columns):
        #        tempArray[row].append(random.randrange(2))
        #return np.array(tempArray)

    @staticmethod
    def displayPattern(lp, pattern, currentCol):
        for y, x in np.ndindex(pattern.shape):
            if x == currentCol and pattern[x, y]:
                lp.grid.led(x, y).color = 'violet'
            elif x == currentCol:
                lp.grid.led(x, y).color = colors.ColorPalette.White.SHADE_6
            elif pattern[x, y]:
                lp.grid.led(x, y).color = 'blue'
            else:
                lp.grid.led(x, y).color = 0

    def displayCurrentCol(self):
        if self.currentCol > 0:
            self.lp.panel.led(Labeled().button_names[self.currentCol - 1]).color = 0
        else:
            self.lp.panel.led(Labeled().button_names[self.COLS - 1]).color = 0
        self.lp.panel.led(Labeled().button_names[self.currentCol]).color = colors.ColorPalette.White.SHADE_6


    def handle_event(self, button_event):
        if not button_event or not button_event.button:
            return
        if button_event.button.name == 'stop_solo_mute' and button_event.type == ButtonEvent.PRESS:
            return
        if button_event.button.name == 'stop_solo_mute' and button_event.type == ButtonEvent.RELEASE:
            self.started = not self.started
            if self.started:
                button_event.button.led.color = colors.ColorPalette.Red.SHADE_9
            else:
                button_event.button.led.color = colors.ColorPalette.Green.SHADE_43
            return

        if button_event.type == ButtonEvent.PRESS:
            self.pattern[button_event.button.x][button_event.button.y - 1] = not self.pattern[button_event.button.x][button_event.button.y -1 ]
            print(button_event.button.x)
            print(button_event.button.y)
            print(self.pattern)
            button_event.button.led.color = random.randint(1, 127)  # Set LED to random color while button is pressed  # noqa
            print(f"Button '{button_event.button.name}' pressed.")
        elif button_event and button_event.type == ButtonEvent.RELEASE:
            button_event.button.led.color = 0  # Turn LED off once button is released  # noqa
            print(f"Button '{button_event.button.name}' released.")
        else:
            sys.exit()  # Exit on KeyboardInterrupt


    def updatePattern(self):
        self.pattern = self.update(self.pattern)
        if np.array_equal(self.pattern, self.oldpattern):
            self.pattern = self.getPattern(self.ROWS,self.COLS)
            self.oldpattern = self.getPattern(self.ROWS,self.COLS)
        else:
            self.oldpattern = self.pattern

    def start(self):
        while True:
            self.displayPattern(self.lp, self.pattern, self.currentCol)
            self.displayCurrentCol()
            time.sleep(.1)
            if self.started:
                if self.currentCol < self.COLS - 1:
                    self.currentCol += 1
                else:
                    self.currentCol = 0
                    self.updatePattern()
            self.handle_event(self.lp.panel.buttons().poll_for_event(timeout=.1))  # Wait for a button press/release  # noqa


if __name__ == '__main__':
    temp = GameOfLifeSeq()
    temp.start()
