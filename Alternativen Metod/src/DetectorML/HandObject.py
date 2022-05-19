import math
import time
import numpy as np
from Handler import helpers


class FingerObject:

    def __init__(self, coords):
        self.coords = coords
        self.isUp = None
        self.orientation = None
        self.parse_coords()


    def parse_coords(self):

        coords = self.coords

        oVec = (coords[3][0]-coords[0][0], coords[3][1]-coords[0][1])
        self.orientation = math.atan(oVec[1]/oVec[0]) if oVec[0] != 0 else math.pi/2

        sVec = np.array([coords[1][0]-coords[0][0], coords[1][1]-coords[0][1]])
        pVec = np.array([coords[3][0]-coords[1][0], coords[3][1]-coords[1][1]])

        angle = (sVec[0]*pVec[0] + sVec[1]*pVec[1])/(np.linalg.norm(sVec)*np.linalg.norm(pVec))
        angle = min((1, max((angle, -1))))
        angle = math.acos(angle)

        self.isUp = angle < 0.4


class HandObject:

    def __init__(self, fingers_data):
        self.finger_coords = fingers_data
        self.fingers = []
        self.orientation = None
        self.pointer = None
        self.pose = None
        self.time = time.time()
        self.parse_coords()


    def parse_coords(self):

        coords = self.finger_coords

        self.fingers = []

        i = 1
        while i <= 20:
            self.fingers.append(FingerObject(coords[i:i+4]))
            i += 4

        vector = (coords[9][0]-coords[0][0], coords[9][1]-coords[0][1])
        self.orientation = math.atan(vector[1]/vector[0]) if vector[0] != 0 else math.pi/2
        self.pointer = coords[8]
        self.pose = helpers.classify(self)

