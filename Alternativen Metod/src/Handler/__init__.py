import os
import subprocess
import numpy as np
import pyautogui
import cv2
from DetectorML import HandObject
import Handler.helpers
from Handler.controller import Controller

controller = Controller()


class Handler:

    def __init__(self):
        self.child = BaseDelegate(self)
        self.event_queue = []


    def set_camera_dims(self, width, height):
        controller.set_camera_dims(width, height)

    def delegate(self, event):
        self.event_queue.append(event)
        if len(self.event_queue) < 3:
            return
        poses = [e.pose for e in self.event_queue]
        if poses.count(event.pose) != 3:
            self.event_queue.pop(0)
            return

        avgX = sum([e.pointer[0] for e in self.event_queue])/3
        avgY = sum([e.pointer[1] for e in self.event_queue])/3
        event.pointer = (avgX, avgY)
        self.child.delegate(event)
        self.event_queue = []


    def handle(self, event):
        if event.pose is None:
            print("unknown pose")
            return
        print('unhandled pose: '+event.pose)


class Delegate:

    def __init__(self, parent):
        self.parent = parent
        self.state = None
        self.child = None


    def delegate(self, event:HandObject):
        if self.child is not None:
            self.child.delegate(event)
        elif self.accept(event):
            self.handle(event)
        else:
            self.parent.handle(event)


    def handle(self, event):
        pass

    def accept(self, event):
        pass

    def closeChild(self):
        self.child = None


class BaseDelegate(Delegate):

    def __init__(self, parent):
        super().__init__(parent)
        self.last_event = None


    def handle(self, event:HandObject):

        last_event = self.last_event
        self.last_event = event

        if event.pose == 'pointer':
            controller.moveMouse(event)
            return

        if last_event is None:
            return

        if event.pose == 'peaceSign':
            if last_event.pose == 'peaceSign':
                return
            pyautogui.doubleClick()

        if event.pose == 'opened':
            if last_event.pose == 'opened':
                return
            pyautogui.press('space')

        if event.pose == 'rock':
            if last_event.pose == 'rock':
                return
            pyautogui.rightClick()

        if event.pose == 'check':
            if last_event.pose == 'check':
                return
            self.child = DragDelegate(self)
            return

        if event.pose == 'spiderman':
            if last_event.pose == 'spiderman':
                return
            self.child = TestDelegate(self)
            return

        if event.pose == 'lastThree':
            if last_event.pose == 'lastThree':
                return
            self.child = ChainDelegate(self,
                                       ['lastThree', 'normalFour', 'opened'],
                                       controller.openVlc
                                       )
            return

        if event.pose == 'closed':
            if last_event.pose == 'closed':
                return
            self.child = ChainDelegate(self,
                                       ['closed', 'opened', 'closed'],
                                       lambda: pyautogui.hotkey('ctrl', 'q')
                                       )
            return


        if event.pose == 'wide':
            if last_event.pose == 'wide':
                return
            pyautogui.hotkey('winleft')
            return

        if event.pose == 'middleThree':
            if last_event.pose == 'middleThree':
                return
            pyautogui.hotkey('winleft', 'd')
            return


    def accept(self, event):
        if event.pose is None:
            return False
        return True


class DragDelegate(Delegate):

    def __init__(self, parent):
        super().__init__(parent)
        pyautogui.mouseDown()


    def handle(self, event):

        controller.moveMouse(event)

        if event.pose != 'check':
            pyautogui.mouseUp()
            self.parent.closeChild()
            return


    def accept(self, event):
        if event.pose is None:
            return False
        return True




class TestDelegate(Delegate):

    def __init__(self, parent):
        super().__init__(parent)
        self.changed = False
        img = np.zeros((100,200), 'uint8')
        cv2.imshow('gesture', img)


    def handle(self, event):

        if event.pose == 'spiderman':
            if not self.changed:
                return
            cv2.destroyWindow('gesture')
            self.parent.closeChild()
            return

        self.changed = True
        text = "?" if event.pose is None else event.pose
        l = len(text)
        img = np.zeros((100, l*20+30), 'uint8')
        cv2.putText(img, event.pose, (10,60), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)
        cv2.imshow('gesture', img)

    def accept(self, event):
        return True


class ChainDelegate(Delegate):

    def __init__(self, parent, chain, action):
        super().__init__(parent)
        self.chain = chain
        self.remaining = [p for p in chain]
        self.action = action
        self.last_event_pose = None

    def handle(self, event):

        if len(self.remaining) == 0:
            self.action()
            self.parent.closeChild()
            return

        last = self.last_event_pose
        self.last_event_pose = event.pose

        if event.pose == last:
            return

        if event.pose != self.remaining[0]:
            self.parent.closeChild()
            for i in range(1, len(self.chain)-len(self.remaining)):
                event.pose = self.chain[i]
                self.parent.handle(event)
            return

        self.remaining.pop(0)

    def accept(self, event):
        return True


