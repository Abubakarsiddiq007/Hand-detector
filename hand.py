import math
import time
import numpy as np # type: ignore
import cv2 # type: ignore
from HandTrackingModule import handDetector # type: ignore
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # type: ignore
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL # type: ignore

cap = cv2.VideoCapture(0)
detector = handDetector(detectionCon=0.7)  # Fixed parameter name and value

# Volume control setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

pTime = 0
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmlist = detector.findPosition(img, draw=False)
    
    # FPS calculation
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), 
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    if len(lmlist) >= 9:  # Check if we have enough landmarks
        # Get thumb and index finger positions
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        # x3, y3 = lmlist[5][1], lmlist[5][2]
        # x4, y4 = lmlist[6][1], lmlist[6][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        # bx, by = (x3 + x4) // 2, (y3 + y4) // 2
        # Draw hand landmarks
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        # cv2.circle(img, (x3, y3), 15, (255, 0, 255), cv2.FILLED)
        # cv2.circle(img, (x4, y4), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        # cv2.line(img, (x3, y3), (x4, y4), (255, 0, 255),3)


        # Calculate distance between fingers
        length = math.hypot(x2 - x1, y2 - y1)
        
        # Volume control
        vol = np.interp(length, [30, 250], [minVol, maxVol])
        volBar = np.interp(length, [30, 250], [400, 150])
        volPer = np.interp(length, [30, 250], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)

        # Change center circle color when close
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            # cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
    # Volume bar drawing (always visible)
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    # cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    # cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

    cv2.putText(img, f'{int(volPer)}%', (40, 450), 
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()