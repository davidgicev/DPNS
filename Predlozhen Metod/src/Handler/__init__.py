import pyautogui

from Classifier import HandObject

pyautogui.FAILSAFE = False
screenWidth, screenHeight = pyautogui.size()


class Handler:

    def __init__(self):
        self.window_width  = None
        self.window_height = None
        self.eventQueue = []
        self.lastEvent = None


    def setWindowDims(self, width, height):
        self.window_width = width
        self.window_height = height


    def handle(self, event:HandObject):

        if event is None:
            return

        self.eventQueue.append(event)
        self.process()


    def process(self):

        if len(self.eventQueue) < 3:
            return

        events = self.eventQueue

        votes = [e.num_fingers for e in events[-3:]]
        if not(votes[0] == votes[1] == votes[2]):
            return

        num_fingers = votes[0]
        print(num_fingers)

        # return

        if num_fingers == 0:
            self.moveMouse(events[-1])

        if self.lastEvent is not None:
            if self.lastEvent.num_fingers == num_fingers:
                return

        self.lastEvent = events[-1]

        if num_fingers == 3:
            pyautogui.press('space')

        if num_fingers == 4:
            pyautogui.press('n')

        if num_fingers == 2:
            self.clickMouse()

        self.eventQueue = []

    def scalePointer(self, pos):

        xScale = screenWidth / self.window_width
        yScale = screenHeight / self.window_height

        sX = int(xScale * pos[0])
        sY = int(yScale * pos[1])

        return sX, sY


    def moveMouse(self, event:HandObject):
        pyautogui.moveTo(*self.scalePointer(event.farthest), _pause=False)

    def clickMouse(self):
        pyautogui.click(_pause=False)
