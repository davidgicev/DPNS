import cv2

from Detector import Detector
from Classifier import Classifier
from Handler import Handler

detector = Detector()
classifier = Classifier()
handler = Handler()

# vid = cv2.VideoCapture('./sample.webm')
vid = cv2.VideoCapture(0)

if vid.isOpened():
    frame_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_width  = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    handler.setWindowDims(frame_width, frame_height)

while vid.isOpened():

    ret, frame = vid.read()
    frame = cv2.flip(frame, 1)

    cv2.imshow('default', frame)

    segmented = detector.process(frame)
    event = classifier.classify(segmented)
    handler.handle(event)

    key = cv2.waitKey(1)
    if key == ord('p'):
        key = cv2.waitKey(-1)
    if key == ord('r'):
        detector.updateBackground(frame)
        continue
    if key == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()
