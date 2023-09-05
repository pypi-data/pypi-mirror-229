import PiKit
import cv2
cap = PiKit.VideoCapture(0)

while True:
    frame = cap.read()
    PiKit.imshow(frame)
    if PiKit.wait('q')==0:
        break

cap.release()