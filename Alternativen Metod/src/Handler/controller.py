import subprocess

import pyautogui

from DetectorML import HandObject


class Controller:

    def __init__(self):
        self.screen_dims = pyautogui.size()
        self.camera_dims = None

    def set_camera_dims(self, width, height):
        self.camera_dims = (width, height)

    def moveMouse(self, event:HandObject):
        pyautogui.moveTo(*self.scale(event.pointer), 0.1, _pause=False)

    def dragTo(self, event:HandObject):
        pyautogui.dragTo(*self.scale(event.pointer), _pause=False, button='left')

    def scale(self, pos):
        xScale = pos[0]*self.screen_dims[0]
        yScale = pos[1]*self.screen_dims[1]

        sX = int(xScale * pos[0])
        sY = int(yScale * pos[1])

        return sX, sY

    def scale_camera(self, pos):
        xScale = pos[0] * self.camera_dims[0]
        yScale = pos[1] * self.camera_dims[1]

        sX = int(xScale * pos[0])
        sY = int(yScale * pos[1])

        return sX, sY


    def openVlc(self):
        subprocess.Popen(['vlc'])

