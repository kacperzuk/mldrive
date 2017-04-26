import sys
import numpy as np
import math
import time
import cv2
from collections import Counter
from threading import Thread

# must be odd number:
CANNY_LOW_THRESHOLD=20
CANNY_HIGH_THRESHOLD=40
HOUGH_INTERSECTIONS=20
HOUGH_MIN_LENGTH=70
HOUGH_MAX_GAP=10

def points_to_hesse_normal_form(p1, p2):
    # https://en.wikipedia.org/wiki/Hesse_normal_form

    q,w = p1
    r,t = p2

    if t != w:
        A = 1
        B = (q-r)/(t-w)
        C = w*(r-q)/(t-w) - q
    elif q != r:
        A = (t-w)/(q-r)
        B = 1
        C = q*(w-t)/(q-r) - w
    else:
        raise Exception("Same points")

    u = math.sqrt(A*A+B*B)
    if C > 0:
      u = -1

    A /= u
    B /= u
    C /= u

    return (A,B,C)

def line_to_points(line, shape):
    # Turns output of points_to_hesse_normal_form into 2 points covering whole frame. 
    H,W,d = shape
    A,B,C = line
    if A == 0:
        p1 = (0, int(-C/B))
        p2 = (W, int(-C/B))
    else:
        p1 = (int(-C/A), 0)
        p2 = (int(-(B*H+C)/A), H)
    return (p1, p2)

def generate_mask(img):
    mask = np.zeros_like(img)
    ignore_mask_color = 255
    w = img.shape[1]
    h = img.shape[0]
    vertices = np.array([
      [0.1*w, 0.8*h],
      [0.3*w, 0.5*h],
      [0.7*w, 0.5*h],
      [0.9*w, 0.8*h]
    ], np.int32)
    cv2.fillPoly(mask, [vertices], ignore_mask_color)
    return mask

def detect_lane(img):
    result = {
        "original": img.copy()
    }

    # these algorithms only work with Gray unfortunately
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    result["gray"] = img.copy()

    mask = generate_mask(img)
    result["mask"] = mask.copy()
    result["masked"] = cv2.bitwise_and(img, mask)
    img = cv2.Canny(img, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD)
    result["canny"] = img.copy()
    img = cv2.bitwise_and(img, mask)
    result["canny_masked"] = img.copy()
    line_segments = cv2.HoughLinesP(img, 1, math.pi/180, HOUGH_INTERSECTIONS, np.array([]), minLineLength=HOUGH_MIN_LENGTH, maxLineGap=HOUGH_MAX_GAP)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if line_segments is None:
        return result
    line_segments = [ l[0] for l in line_segments ]
    result["segments_d"] = line_segments

    if len(line_segments) > 2:
        # merge similar lines using kmeans clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, .5)
        flags = cv2.KMEANS_RAND_CENTERS
        centers = [ ( (l[0]+l[2])/2, (l[1]+l[3])/2) for l in line_segments ]
        count = min(5, len(centers))
        compactness,labels,centers = cv2.kmeans(np.float32(centers),count,None,criteria,10,flags)
        labels = [ l[0] for l in labels.tolist() ]
        lines = []
        for i in range(count):
            a = 0
            b = 0
            c = 0
            d = 0
            l = 0
            for j in range(len(labels)):
                if labels[j] == i:
                    t = line_segments[j]
                    sl = math.sqrt(math.pow(t[0] - t[2], 2) + math.pow(t[1] - t[3], 2))
                    l += sl
                    a += sl*t[0]
                    b += sl*t[1]
                    c += sl*t[2]
                    d += sl*t[3]
            lines.append((a/l, b/l, c/l, d/l))
    else:
        return result

    lines = [ points_to_hesse_normal_form((s[0], s[1]), (s[2], s[3])) for s in lines ]
    # merge lines with angle < math.pi/30
    # that can be problematic, we should also check something else here
    for l1 in lines:
        for l2 in lines:
            if l1 == l2:
                continue
            try:
                lines.index(l1)
                lines.index(l2)
            except ValueError:
                continue
            if abs(math.atan2(l1[1], l1[0]) - math.atan2(l2[1], l2[0])) < math.pi/30:
                l3 = ((l1[0]+l2[0])/2, (l1[1]+l2[1])/2, (l1[2]+l2[2])/2)
                lines.remove(l1)
                lines.remove(l2)
                lines.append(l3)
    lines = [ line_to_points(l, img.shape) for l in lines ]
    lines = [ (l[0][0], l[0][1], l[1][0], l[1][1]) for l in lines ]
    lines = sorted(lines, key=lambda l: abs(l[0] - l[2]))
    result["clustered_lines"] = lines
    return result


def draw_it(result):
    base = result["original"]
    #base = result["masked"]
    if len(base.shape) != 3:
        base = cv2.cvtColor(base, cv2.COLOR_GRAY2RGB)
    try:
        for line in result["segments_d"]:
            base = cv2.line(base, (line[0], line[1]), (line[2], line[3]), (255,0,0), 2)
    except KeyError:
        pass
    try:
        for line in result["clustered_lines"][2:]:
            p1 = (line[0], line[1])
            p2 = (line[2], line[3])
            base = cv2.line(base, p1, p2, (0,0,255), 2)
        for line in result["clustered_lines"][:2]:
            p1 = (line[0], line[1])
            p2 = (line[2], line[3])
            base = cv2.line(base, p1, p2, (0,255,0), 2)
    except KeyError:
        print("No clustered_lines :(")
    return base

cap = cv2.VideoCapture('in.mp4')
if not cap.isOpened():
    raise Exception("Couldn't open cam!")

rv, img = cap.read()
rv, img = cap.read()
rv, img = cap.read()
rv, img = cap.read()
rv, img = cap.read()
rv, img = cap.read()
rv, img = cap.read()
rv, img = cap.read()
sys.stderr.write("Frame size: %dx%d\n" % (img.shape[1], img.shape[0]))
writer = cv2.VideoWriter("out.mp4", cv2.VideoWriter_fourcc('m', 'p', 'g', '1'), 30, (img.shape[1], img.shape[0]))
while True:
    rv, img = cap.read()
    if not rv:
        time.sleep(0.01)
        continue

    result = detect_lane(img)
    img = draw_it(result)
    cv2.imshow('image', img)
    writer.write(img)
    if chr(cv2.waitKey(0)) == 'q':
        break

cv2.destroyAllWindows()
