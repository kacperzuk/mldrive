import math
import numpy as np
import cv2

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
        return None

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
    if A != 0:
        if (E - D*B/A) != 0:
            y = (D*C/A - F)/(E - D*B/A)
            x = -(B*y + C)/A
        else:
            return None
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
    #vertices = np.array([
    #  [0.0*w, 0.7*h],
    #  [0.2*w, 0.2*h],
    #  [0.9*w, 0.1*h],
    #  [1.0*w, 0.7*h]
    #], np.int32)
    vertices = np.array([
      [0.0*w, 0.4*h],
      [0*w, 1*h],
      [1*w, 1*h],
      [1*w, 0.4*h]
    ], np.int32)
    cv2.fillPoly(mask, [vertices], ignore_mask_color)
    return mask

def avg_line_distance(shape, a, b):
    h = shape[0]
    w = shape[1]
    hdists = []
    for h in ( 0, h/2, h ):
        p1 = intersection_point(a, [0, 1, -h])
        p2 = intersection_point(b, [0, 1, -h])
        if p1 is None or p2 is None:
            hdists.append(math.inf)
        else:
            hdists.append(abs(p1[0]-p2[0]))
    wdists = []
    for w in ( 0, w/2, w ):
        p1 = intersection_point(a, [1, 0, -w])
        p2 = intersection_point(b, [1, 0, -w])
        if p1 is None or p2 is None:
            wdists.append(math.inf)
        else:
            wdists.append(abs(p1[1]-p2[1]))
    return min(sum(wdists)/len(wdists), sum(hdists)/len(hdists))

def merge_lines(a,b,w=0.5):
    return [ int(w*a[i] + (1 - w)*b[i]) for i in range(len(a)) ]
