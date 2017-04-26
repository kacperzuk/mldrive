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
HOUGH_MIN_LENGTH=60
HOUGH_MAX_GAP=15

def segment_to_hesse_normal_form(segment):
    # https://en.wikipedia.org/wiki/Hesse_normal_form
    q,w,r,t = segment

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
    # Turns output of segment_to_hesse_normal_form into 2 points covering whole frame. 
    H,W,d = shape
    A,B,C = line
    if A == 0:
        q, w = (0, int(-C/B))
        r, t = (W, int(-C/B))
    elif B == 0:
        q, w = (int(-C/A), 0)
        r, t = (int(-C/A), H)
    else:
        ps = [
            (int(-C/A), 0),
            (int(-(B*H+C)/A), H),
            (0, int(-C/B)),
            (W, int(-(A*W+C)/B))
        ]
        res = []
        for p in ps:
            if p[0] >= 0 and p[0] <= W and p[1] >= 0 and p[1] <= H:
                res.append(p)
        q, w = res[0]
        r, t = res[1]

    return (q, w, r, t)

def generate_mask(img):
    mask = np.zeros_like(img)
    ignore_mask_color = 255
    w = img.shape[1]
    h = img.shape[0]
    # behind
    #vertices = np.array([
    #  [0.1*w, 0.8*h],
    #  [0.3*w, 0.5*h],
    #  [0.7*w, 0.5*h],
    #  [0.9*w, 0.8*h]
    #], np.int32)
    # behind offset
    #vertices = np.array([
    #  [0.1*w, 0.5*h],
    #  [0.2*w, 0.1*h],
    #  [0.7*w, 0.1*h],
    #  [0.8*w, 0.5*h]
    #], np.int32)
    # front angled
    vertices = np.array([
      [0.0*w, 0.7*h],
      [0.2*w, 0.2*h],
      [0.9*w, 0.1*h],
      [1.0*w, 0.7*h]
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

    # extrapolate segments to frame-long lines
    lines = [ segment_to_hesse_normal_form(s) for s in line_segments ]
    lines = [ line_to_points(l, img.shape) for l in lines ]

    if len(lines) > 2:
        # merge similar lines using kmeans clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, .5)
        flags = cv2.KMEANS_RANDOM_CENTERS
        count = min(3, len(lines))
        compactness,labels,lines = cv2.kmeans(np.float32(lines),count,None,criteria,10,flags)
    else:
        return result

    # we prefer vertical lines
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
sys.stderr.write("Frame size: %dx%d\n" % (img.shape[1], img.shape[0]))
writer = cv2.VideoWriter("out.mp4", cv2.VideoWriter_fourcc('x', '2', '6', '4'), 30, (img.shape[1], img.shape[0]))
while True:
    rv, img = cap.read()
    if not rv:
        continue
    result = detect_lane(img)
    img = draw_it(result)
    cv2.imshow('image', img)
    writer.write(img)
    if chr(cv2.waitKey(1000//30)) == 'q':
        break

cv2.destroyAllWindows()
