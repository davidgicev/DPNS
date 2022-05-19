import cv2
import math


class HandObject:

    def __init__(self, num_fingers, points):
        self.num_fingers = num_fingers
        self.centroid = points[0]
        self.farthest = points[1]


    def valid(self):
        if 1 <= self.num_fingers <= 5:
            return True
        return False


class Classifier:

    def classify(self, segmented):

        if segmented is None:
            return
        
        contour, img, points = segmented

        num_fingers = self.countFingers(contour)

        return HandObject(num_fingers, points)


    def countFingers(self, res):

        hull = cv2.convexHull(res, returnPoints=False)
        if len(hull) <= 3:
            return 0

        defects = cv2.convexityDefects(res, hull)
        if defects is not None:
            br = 0
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i][0]
                start = tuple(res[s][0])
                end = tuple(res[e][0])
                far = tuple(res[f][0])
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

                if min((b, c)) < 20:    # ne e dovolno dlaboka vdlabnatinata
                    continue

                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
                if angle <= math.pi * 0.5:
                    br += 1
            if br > 0:
                return br + 1
            else:
                return 0