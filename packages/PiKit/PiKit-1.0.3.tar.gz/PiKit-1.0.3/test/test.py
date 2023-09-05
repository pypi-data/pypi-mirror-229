import PiKit

cap = PiKit.VideoCapture(0)

while True:
    frame = cap.read()
    PiKit.imshow(frame)
    if  0xFF == ord('q'):
        break
cap.release()