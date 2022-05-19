import cv2
import mediapipe

from DetectorML.HandObject import HandObject

handmodel = mediapipe.solutions.hands


class DetectorML:

    def __init__(self, min_detect_conf=0.5, min_track_conf=0.5):
        self.Model = handmodel.Hands(False, 1, min_detect_conf, min_track_conf)


    def process(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.Model.process(frame)
        landmarks = output.multi_hand_landmarks

        if not landmarks or len(landmarks) == 0:
            return

        landmarks = landmarks[0].landmark

        yScale, xScale, _ = frame.shape

        fingers = [(l.x, l.y) for l in landmarks]

        for f in fingers:
            cv2.circle(frame, (int(f[0]*xScale), int(f[1]*yScale)), 10, (255,0,0))

        cv2.imshow('fingers', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        return HandObject(fingers)
