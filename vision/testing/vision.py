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
HOUGH_MIN_LENGTH=50
HOUGH_MAX_GAP=20
LANE_DETECT_HEIGHT=150
LINE_MERGE_ANGLE_DEGREES=10
# behind
LANE_DETECT_HEIGHT=210

def line_angle(l):
    return math.atan2(l[0], l[1])

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

def intersection_point(l1, l2):
    A,B,C = l1
    D,E,F = l2
    if A != 0 and (E - D*B/A) != 0:
        y = (D*C/A - F)/(E - D*B/A)
        x = -(B*y + C)/A
    elif (D - E*A/B) != 0:
        x = (E*C/B - F)/(D - E*A/B)
        y = -(C + A*x)/B
    else:
        return None # parallel lines
    return (int(x),int(y))

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

    # make sure the first point is below the second
    if w < t:
        return (r, t, q, w)
    else:
        return (q, w, r, t)

def generate_mask(img):
    mask = np.zeros_like(img)
    ignore_mask_color = 255
    w = img.shape[1]
    h = img.shape[0]
    # behind
    #vertices = np.array([
    #  [0.6*w, 0.6*h],
    #  [0.4*w, 0.6*h],
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
    result["segments"] = line_segments

    # extrapolate segments to frame-long lines
    lines = [ segment_to_hesse_normal_form(s) for s in line_segments ]
    lines = [ line_to_points(l, img.shape) for l in lines ]
    result["lines"] = line_segments

    if len(lines) > 2:
        # merge similar lines using kmeans clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, .5)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness,labels,lines = cv2.kmeans(np.float32(lines),3,None,criteria,10,flags)
    else:
        return result

    # we prefer vertical lines
    lines = sorted(lines, key=lambda l: abs(l[0] - l[2]))
    result["clustered_lines"] = lines
    if len(lines) > 1:
        h = (0,1,-LANE_DETECT_HEIGHT)
        l1 = lines[0]
        l2 = lines[1]
        # make sure the first line is the left one
        if l1[0] > l2[0]:
            l1 = lines[1]
            l2 = lines[0]

        l1 = segment_to_hesse_normal_form(l1)
        l2 = segment_to_hesse_normal_form(l2)
        p1 = intersection_point(l1, h)
        p2 = intersection_point(l2, h)
        result["intersections"] = ( p1,p2, line_to_points(h, img.shape))
        result["center"] = ((p1[0] + p2[0])//2, (p1[1] + p2[1])//2)
    return result

def draw_direction(img, center):
    c = img.shape[1]//2
    x = center[0]
    y = center[1]

    p1 = (x, y+15)
    p2 = (c, y+15)
    img = cv2.line(img, p1, p2, (0, 255, 255), 3)
    if x > c:
        p1 = (c+5,y+10)
        img = cv2.line(img, p1, p2, (0, 255, 255), 3)
        p1 = (c+5,y+20)
        img = cv2.line(img, p1, p2, (0, 255, 255), 3)
    else:
        p1 = (c-5,y+10)
        img = cv2.line(img, p1, p2, (0, 255, 255), 3)
        p1 = (c-5,y+20)
        img = cv2.line(img, p1, p2, (0, 255, 255), 3)
    cv2.imshow('image',img)
    if abs(c-x) > 50:
        if chr(cv2.waitKey(0)) == 'q':
            sys.exit(0)
    return img


def draw_it(result):
    base = result["original"]
    #base = result["masked"]
    if len(base.shape) != 3:
        base = cv2.cvtColor(base, cv2.COLOR_GRAY2RGB)
    try:
        for line in result["segments"]:
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
    try:
        line = result["intersections"][2]
        p1 = (line[0], line[1])
        p2 = (line[2], line[3])
        base = cv2.line(base, p1, p2, (50,50,50), 2)
        base = cv2.circle(base, result["intersections"][0], 5, (255,0,255), -1)
        base = cv2.circle(base, result["intersections"][1], 5, (255,0,255), -1)
        base = cv2.circle(base, result["center"], 10, (255,255,0), -1)
        draw_direction(base, result["center"])
    except KeyError:
        print("No intersections :(")
    return base

if __name__ == "__main__":
    cap = cv2.VideoCapture('in.mp4')
    if not cap.isOpened():
        raise Exception("Couldn't open cam!")

    rv, img = cap.read()
    sys.stderr.write("Frame size: %dx%d\n" % (img.shape[1], img.shape[0]))
    writer = cv2.VideoWriter("out.mp4", cv2.VideoWriter_fourcc('x', '2', '6', '4'), 30, (img.shape[1], img.shape[0]))
    while True:
        print("Next")
        rv, img = cap.read()
        if not rv:
            break
        result = detect_lane(img)
        img = draw_it(result)
        cv2.imshow('image', img)
        writer.write(img)
        if chr(cv2.waitKey(1000//30)) == 'q':
            break
        #if chr(cv2.waitKey(0)) == 'q':
        #    break

    cv2.destroyAllWindows()
