from time import sleep
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import serial.tools.list_ports as ports
from serial import Serial
from time import sleep

region = {
  "N": [ 12347, 56713, 78123 ],
  "C": [ 11120, 10420 ],
  "S": [ 89760, 45678 ],
  "E": [ 12459, 12398 ],
}

# Find COM port
comport = None
comlist = ports.comports()
for element in comlist:
    comport = element.device
if not comport:
    print("Not found COM port")
    exit()

ser = Serial(comport, 9600, timeout=0.1)

def findRegion(postcode):
    """
    for x in [ "N", "C", "S", "E" ]:
        for i in region[x]:
            if i == postcode:
                return x
    """
    first2digi = None
    try:
        first2digi = int(postcode[:2])
    except:
        return None
    if first2digi >= 50 and first2digi <= 58:
        return b"N"
    elif first2digi >= 20 and first2digi <= 27:
        return b"E"
    elif first2digi >= 80 and first2digi <= 96:
        return b"S"
    elif (first2digi >= 10 and first2digi <= 18) or first2digi == 26 or first2digi == 30 or (first2digi >= 60 and first2digi <= 67) or (first2digi >= 71 and first2digi <= 75) :
        return b"C"

    return None

last_barcode = None
def decoder(image):
    global last_barcode
    gray_img = cv2.cvtColor(image,0)
    barcode = decode(gray_img)

    barCode = None
    for obj in barcode:
        points = obj.polygon
        (x,y,w,h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 0), 3)

        barcodeData = obj.data.decode("utf-8")
        barcodeType = obj.type
        string = "Data " + str(barcodeData) + " | Type " + str(barcodeType)
        
        cv2.putText(frame, string, (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0), 2)
        # print("Barcode: "+barcodeData +" | Type: "+barcodeType)
        barCode = barcodeData

    # if barCode and barCode != last_barcode:
    if barCode:
        postcode = barCode[:5]
        print("Postcode: {}".format(postcode))
        r = findRegion(postcode)
        if r == None:
            r = b"U"
        ser.write(r)
        print("Region: {}".format(r))
        last_barcode = barCode
        sleep(1)

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    decoder(frame)
    cv2.imshow('Image', frame)
    code = cv2.waitKey(10)
    if code == ord('q'):
        break
    