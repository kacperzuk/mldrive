import sys
import numpy as np
import math
import time
import cv2

# must be odd number:
CANNY_LOW_THRESHOLD=150
CANNY_HIGH_THRESHOLD=200

def detect_lane(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    mask = np.zeros_like(img)
    ignore_mask_color = 255
    w = img.shape[1]
    h = img.shape[0]
    vertices = np.array([
      [0.1*w, 0.9*h],
      [0.2*w, 0.4*h],
      [0.8*w, 0.4*h],
      [0.9*w, 0.9*h]
    ], np.int32)
    cv2.fillPoly(mask, [vertices], ignore_mask_color)

    #return None, mask # show just mask
    #return None, cv2.bitwise_and(img, mask) # show masked image

    img = cv2.Canny(img, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD)
    #return None, img # show canny result
    img = cv2.bitwise_and(img, mask)
    line_segments = cv2.HoughLinesP(img, 1, math.pi/180, 20, np.array([]), minLineLength=30, maxLineGap=100)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if line_segments is None:
        print("Frame skip - no line segments from HoughLines")
        return None, img

    for line in line_segments:
        line = line[0]
        img = cv2.line(img, (line[0], line[1]), (line[2], line[3]), (255,0,0), 2)
    #return None, img # show segments

    lines = []
    for l in line_segments:
        l = l[0]
        if l[2] - l[0] == 0:
            continue
        a = (l[3] - l[1])/(l[2] - l[0])
        b = l[1] - a*l[0]
        lines.append([a, b])

    if len(lines) > 2:
        # merge similar lines
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness,labels,centers = cv2.kmeans(np.array(lines, np.float32),min(4,len(lines)),None,criteria,10,flags)
        if centers is not None:
            lines = centers

    if lines is None:
        print("Frame skip - no lines :(")
        for line in line_segments:
            line = line[0]
            img = cv2.line(img, (line[0], line[1]), (line[2], line[3]), (255,0,0), 2)
        return None, img

    plines = []
    for line in lines:
        a = line[0]
        b = line[1]
        if a == 0:
            p1 = (0, int(b))
            p2 = (img.shape[1], int(b))
        else:
            try:
                p1 = (int((img.shape[0]*0.3-b)/a), int(img.shape[0]*0.3))
                p2 = (int((img.shape[0]-b)/a), img.shape[0])
            except OverflowError:
                return None, None
        plines.append((p1,p2))
    return plines, None

def draw_lines(img, lines):
    for line in lines:
        p1 = line[0]
        p2 = line[1]
        img = cv2.line(img, p1, p2, (0,255,0), 2)
    return img

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Couldn't open cam!")

rv, img = cap.read()
sys.stderr.write("Frame size: %dx%d\n" % (img.shape[1], img.shape[0]))
while True:
    rv, img = cap.read()
    if not rv:
        time.sleep(0.01)
        continue

    img = cv2.resize(img, (640, 360))

    lines, debug = detect_lane(img)
    if lines:
        img = draw_lines(img, lines)
    else:
        img = debug
    if img is not None:
        if sys.stdout.isatty():
            cv2.imshow('image', img)
        else:
            sys.stdout.buffer.write(img.tostring())
    if chr(cv2.waitKey(1)) == 'q':
        break

cv2.destroyAllWindows()
