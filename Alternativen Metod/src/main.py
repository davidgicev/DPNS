import cv2
from DetectorML import DetectorML
from Handler import Handler

detector = DetectorML()
handler = Handler()

vid = cv2.VideoCapture(0)

if vid.isOpened():
    frame_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_width  = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    # handler.setWindowDims(frame_width, frame_height)

handler.set_camera_dims(frame_width, frame_height)

while vid.isOpened():

    ret, frame = vid.read()
    frame = cv2.flip(frame, 1)
    res = detector.process(frame)
    if res is not None:
        handler.delegate(res)


    key = cv2.waitKey(1)
    if key == ord('p'):
        key = cv2.waitKey(-1)
    if key == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()
