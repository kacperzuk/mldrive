import numpy as np
import math
import time
import cv2

# must be odd number:
GAUSS_KERNEL_SIZE=5

CANNY_LOW_THRESHOLD=150
CANNY_HIGH_THRESHOLD=200

for i in range(1):
    img = cv2.imread('test-imgs/2.jpg',0)
    org = img.copy()
    org = cv2.cvtColor(org, cv2.COLOR_GRAY2RGB)
    #Blur, we only want trully contrasting stuff to stand out, not artifacts
    img = cv2.GaussianBlur(img, (GAUSS_KERNEL_SIZE, GAUSS_KERNEL_SIZE), 0)
    #Edge detection!
    img = cv2.Canny(img, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD)
    #Trim to what's in front
    mask = np.zeros_like(img)
    ignore_mask_color = 255
    vertices = np.array([
      [100, 260],
      [230, 130],
      [400, 130],
      [530, 260]
    ], np.int32)
    cv2.fillPoly(mask, [vertices], ignore_mask_color)
    img = cv2.bitwise_and(img, mask)
    #Lines detection
    line_segments = cv2.HoughLinesP(img, 1, math.pi/180, 20, np.array([]), minLineLength=30, maxLineGap=100)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    with_segments = img.copy()
    if line_segments is None:
        print("Frame skip - no line segments from HoughLines")
        continue
    for line in line_segments:
        line = line[0]
        with_segments = cv2.line(with_segments, (line[0], line[1]), (line[2], line[3]), (255,0,0), 2)
    #get a,b of lines
    lines = []
    for l in line_segments:
        l = l[0]
        #a = np.arctan2(l[3]-l[1], l[2]-l[0])
        a = (l[3] - l[1])/(l[2] - l[0])
        b = l[1] - a*l[0]
        lines.append([a, b])
    # merge similar lines
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    compactness,labels,centers = cv2.kmeans(np.array(lines, np.float32),min(4,len(lines)),None,criteria,10,flags)
    lines = centers
    if lines is None:
        print("Frame skip - no clusters from kmeans")
        continue
    plines = []
    for line in lines:
        a = line[0]
        b = line[1]
        try:
            p1 = (int((130-b)/a), 130)
            p2 = (int((img.shape[0]-b)/a), img.shape[0])
        except OverflowError:
            continue
        plines.append((p1,p2))
    plines.sort(key=lambda x: x[1][0])
    lline = None
    rline = None
    for line in plines:
        if line[1][0] < img.shape[0]/2 and line[1][0] < line[0][0]:
            lline = line
        if not rline and line[1][0] > img.shape[0]/2 and line[1][0] > line[0][0]:
            rline = line
    d = (rline, lline)
    if not rline or not lline:
        d = plines
        print("No rline or lline")
    for line in d:
        p1 = line[0]
        p2 = line[1]
        img = cv2.line(img, p1, p2, (0,255,0), 2)
        org = cv2.line(org, p1, p2, (0,255,0), 2)
    cv2.imshow('image',org)
    cv2.waitKey(0)
cv2.destroyAllWindows()
