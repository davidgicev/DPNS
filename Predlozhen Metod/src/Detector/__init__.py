import math
import cv2
import numpy as np

from Detector.skin_module import SkinModule


class Detector:

    def __init__(self, right_side=False):
        self.fullB = None
        self.skinModule = SkinModule()
        self.right_side_m = right_side


    def updateBackground(self, frame):
        background = cv2.GaussianBlur(frame, (3,3), 0)
        self.fullB = cv2.split(cv2.cvtColor(background, cv2.COLOR_BGR2HSV_FULL))


    def process(self, frame):

        if self.fullB is None:
            self.updateBackground(frame)
            return

        frame = cv2.GaussianBlur(frame, (3,3), 0)
        fullF = cv2.split(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL))
        diffV = cv2.absdiff(self.fullB[2], fullF[2])

        # cv2.imshow('diffV', diffV)
        # cv2.imshow('samoH', fullF[0])
        # cv2.imshow('samoS', fullF[1])
        # cv2.imshow('samoV', fullF[2])

        skinH = self.skinModule.filterHue(fullF[0])
        skinV = self.skinModule.filterVal(fullF[2])

        # cv2.imshow('skinV', skinV)
        # cv2.imshow('skinH', skinH)

        pomV = cv2.bitwise_and(skinV, diffV)
        pomH = cv2.bitwise_and(skinH, diffV)

        # cv2.imshow('andV', pomV)
        # cv2.imshow('andH', pomH)

        threshH = self.skinModule.calculateHueThresh()
        _, pomH = cv2.threshold(pomH, threshH, 255, cv2.THRESH_BINARY)
        threshV = self.skinModule.calculateValThresh()
        _, pomV = cv2.threshold(pomV, threshV, 255, cv2.THRESH_BINARY)

        combined = cv2.bitwise_or(pomV, pomH)

        tempkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        combined = cv2.erode(combined, tempkernel)
        combined = cv2.dilate(combined, tempkernel)

        # cv2.imshow('pomn', combined)
        # cv2.imshow('pomV', pomV)
        # cv2.imshow('pomH', pomH)

        maskedHuepom = cv2.bitwise_and(fullF[0], combined)
        maskedValpom = cv2.bitwise_and(fullF[2], combined)

        self.skinModule.calculateNewHueRange(maskedHuepom)
        self.skinModule.calculateNewValRange(maskedValpom)

        wrapper = cv2.dilate(combined, np.ones((5,5), 'uint8'), iterations=10)
        contours, _ = cv2.findContours(wrapper, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        wrapper = np.zeros(wrapper.shape, 'uint8')
        cv2.drawContours(wrapper, contours, 0, (255, 255, 255), cv2.FILLED)

        if len(contours) == 0:
            return

        pomWrapper = cv2.bitwise_and(wrapper, combined)
        cwc, _ = cv2.findContours(pomWrapper, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cwc = sorted(cwc, key=cv2.contourArea, reverse=True)

        cv2.imshow('wrapper', wrapper)

        approx = cv2.approxPolyDP(contours[0], 10, True)
        M = cv2.moments(approx)

        if M["m00"] == 0:
            return

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        centroid = (cX, cY)

        frameCopy = frame
        cv2.drawContours(frameCopy, [approx], -1, (0, 255, 255))

        [vx, vy, x, y] = cv2.fitLine(approx, cv2.DIST_L2, 0, 0.01, 0.01)
        koef = vy / vx
        b = (x, y)

        points = [p[0] for p in approx]

        leftmost  = int((-x * vy / vx) + y)
        rightmost = int(((wrapper.shape[1] - x) * vy / vx) + y)

        cv2.line(frameCopy, (wrapper.shape[1] - 1, rightmost), (0, leftmost), 255, 2)

        minBoundRect = cv2.minAreaRect(approx)
        wh = minBoundRect[1]
        cKoef = max((wh[0] / wh[1], wh[1] / wh[0]))

        if self.right_side_m:
            farthest = max(points, key=lambda p: math.dist(p, (wrapper.shape[1] - 1, rightmost)))
        else:
            farthest = max(points, key=lambda p: math.dist(p, (0, leftmost)))

        closest = max(points, key=lambda p: math.dist(p, farthest))

        if cKoef < 1.2:
            if self.right_side_m:
                closest = min(points, key=lambda p: math.dist(p, (wrapper.shape[1] - 1, rightmost)))
            else:
                closest = min(points, key=lambda p: math.dist(p, (0, leftmost)))
            mask = wrapper
            pref = 0.5
            midpoint = (int(sum((pref * closest[0], (1 - pref) * farthest[0]))),
                        int(sum((pref * closest[1], (1 - pref) * farthest[1]))))

            cv2.circle(frameCopy, midpoint, int(math.dist(farthest, closest) * 0.5), (3, 252, 102))

            mask = np.zeros(wrapper.shape, 'uint8')
            cv2.circle(mask, midpoint, int(math.dist(farthest, closest) * 0.5), (255, 255, 255),
                       thickness=cv2.FILLED)

            cv2.circle(frameCopy, tuple(farthest), 10, (0, 100, 0), -1)
            centroid = closest
        else:

            pref = 0.55
            midpoint = (int(sum((pref * farthest[0], (1 - pref) * cX))),
                        int(sum((pref * farthest[1], (1 - pref) * cY))))

            cv2.circle(frameCopy, midpoint, int(math.dist(farthest, (cX, cY)) * 0.5), (3, 252, 102))

            mask = np.zeros(wrapper.shape, 'uint8')
            cv2.circle(mask, midpoint, int(math.dist(farthest, centroid) * 0.5), (255, 255, 255),
                       thickness=cv2.FILLED)

            cv2.circle(frameCopy, tuple(farthest), 10, (0, 0, 200), -1)

        cv2.circle(frameCopy, tuple(centroid), 10, (0, 255, 0), -1)

        palm = cv2.bitwise_and(wrapper, mask)
        palm = cv2.bitwise_and(palm, combined)

        maskedHuepom = cv2.bitwise_and(fullF[0], palm)
        maskedValpom = cv2.bitwise_and(fullF[2], palm)

        self.skinModule.calculateNewHueRange(maskedHuepom)
        self.skinModule.calculateNewValRange(maskedValpom)

        contours, _ = cv2.findContours(palm, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return

        for c in contours:
            for p in c:
                cpX = p[0][0]
                cpY = p[0][1]
                cv2.line(palm, (int(cpX), int(cpY)), tuple(centroid), (255, 255, 255), 2)
                # cv2.line(palm, (int(cpX), int(cpY)), (0, leftmost), (255, 255, 255), 2)

        palm = cv2.dilate(palm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))

        cv2.imshow('palm', palm)
        cv2.imshow('points', frameCopy)

        contours, _ = cv2.findContours(palm, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        target = max(contours, key=cv2.contourArea)

        points = [c for con in cwc for c in con[0]]

        if self.right_side_m:
            farthest = max(points, key=lambda p: math.dist(p, (wrapper.shape[1] - 1, rightmost)))
        else:
            farthest = max(points, key=lambda p: math.dist(p, (0, leftmost)))

        cv2.circle(frameCopy, tuple(farthest), 10, (0, 0, 100), -1)

        if cv2.contourArea(target) > 20000:
            return

        return target, frameCopy, (centroid, farthest)
