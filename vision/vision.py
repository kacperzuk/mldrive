import sys
import numpy as np
import math
import time
import cv2
import paho.mqtt.client as mqtt
from threading import Thread

# must be odd number:
DEVICE_ID=sys.argv[1]
CANNY_LOW_THRESHOLD=150
CANNY_HIGH_THRESHOLD=200
HOUGH_INTERSECTIONS=40
HOUGH_MIN_LENGTH=70
HOUGH_MAX_GAP=40
# possible: mask, masked, canny, hough, final
OUTPUT_MODE="final"
LANE_DETECT_HEIGHT=150
LINE_MERGE_ANGLE_DEGREES=30

mqttc = mqtt.Client()

def on_message(client, userdata, message):
    global CANNY_LOW_THRESHOLD
    global CANNY_HIGH_THRESHOLD
    global OUTPUT_MODE
    global HOUGH_MAX_GAP
    global HOUGH_MIN_LENGTH
    global HOUGH_INTERSECTIONS
    global LANE_DETECT_HEIGHT

    topic = message.topic.split("/")[3:]
    if topic[0] == "canny":
        if topic[1] == "low":
            CANNY_LOW_THRESHOLD = int(message.payload)
            sys.stderr.write("CANNY_LOW_THRESHOLD=%d\n" % CANNY_LOW_THRESHOLD)
            return
        elif topic[1] == "high":
            CANNY_HIGH_THRESHOLD = int(message.payload)
            sys.stderr.write("CANNY_HIGH_THRESHOLD=%d\n" % CANNY_HIGH_THRESHOLD)
            return
    elif topic[0] == "output_mode":
        OUTPUT_MODE = message.payload.decode("utf-8")
        sys.stderr.write("OUTPUT_MODE=%s\n" % OUTPUT_MODE)
        return
    elif topic[0] == "hough":
        if topic[1] == "intersections":
            HOUGH_INTERSECTIONS = int(message.payload)
            sys.stderr.write("HOUGH_INTERSECTIONS=%d\n" % HOUGH_INTERSECTIONS)
            return
        elif topic[1] == "min_length":
            HOUGH_MIN_LENGTH = int(message.payload)
            sys.stderr.write("HOUGH_MIN_LENGTH=%d\n" % HOUGH_MIN_LENGTH)
            return
        if topic[1] == "max_gap":
            HOUGH_MAX_GAP = int(message.payload)
            sys.stderr.write("HOUGH_MAX_GAP=%d\n" % HOUGH_MAX_GAP)
            return
    elif topic[0] == "lane_detect_height":
        LANE_DETECT_HEIGHT = int(message.payload)
        sys.stderr.write("LANE_DETECT_HEIGHT=%d\n" % LANE_DETECT_HEIGHT)
        return
    elif topic[0] == "line_merge_angle":
        LINE_MERGE_ANGLE_DEGREES = int(message.payload)
        sys.stderr.write("LINE_MERGE_ANGLE_DEGREES=%d\n" % LINE_MERGE_ANGLE_DEGREES)
        return
    sys.stderr.write("Unhandled MQTT topic: %s\n" % "/".join(topic))

def on_connect(client, userdata, flags, rc):
    topic = "%s/setconf/vision/#" % DEVICE_ID
    client.subscribe(topic)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.connect_async("127.0.0.1", port=1883)
mqttc.loop_start()

def dump_conf(mqttc):
    global CANNY_LOW_THRESHOLD
    global CANNY_HIGH_THRESHOLD
    global OUTPUT_MODE
    global HOUGH_MAX_GAP
    global HOUGH_MIN_LENGTH
    global HOUGH_INTERSECTIONS
    global LANE_DETECT_HEIGHT
    global LINE_MERGE_ANGLE_DEGREES
    global DEVICE_ID

    prefix = "%s/conf/vision" % DEVICE_ID
    while True:
        mqttc.publish("%s/camera_stream/0" % DEVICE_ID, "ws://192.168.2.237:8084")
        mqttc.publish("%s/canny/low" % prefix, CANNY_LOW_THRESHOLD)
        mqttc.publish("%s/canny/high" % prefix, CANNY_HIGH_THRESHOLD)
        mqttc.publish("%s/hough/max_gap" % prefix, HOUGH_MAX_GAP)
        mqttc.publish("%s/hough/intersections" % prefix, HOUGH_INTERSECTIONS)
        mqttc.publish("%s/hough/min_length" % prefix, HOUGH_MIN_LENGTH)
        mqttc.publish("%s/output_mode" % prefix, OUTPUT_MODE)
        mqttc.publish("%s/lane_detect_height" % prefix, LANE_DETECT_HEIGHT)
        mqttc.publish("%s/line_merge_angle" % prefix, LINE_MERGE_ANGLE_DEGREES)
        time.sleep(1)

Thread(target=dump_conf, args=(mqttc,)).start()

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
      [0.0*w, 0.75*h],
      [0.1*w, 0.2*h],
      [0.9*w, 0.2*h],
      [1.0*w, 0.75*h]
    ], np.int32)
    cv2.fillPoly(mask, [vertices], ignore_mask_color)
    return mask

def avg_line_distance(shape, a, b):
    h = img.shape[0]
    w = img.shape[1]
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
        k = min(5, len(lines))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, .5)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness,labels,lines = cv2.kmeans(np.float32(lines),k,None,criteria,10,flags)
    else:
        return result

    lines = lines.tolist()
    found = True
    while found:
        found = False
        for a in lines:
            ah = segment_to_hesse_normal_form(a)
            if ah is None:
                lines.remove(a)
                continue
            for b in lines:
                if a == b:
                    continue
                if b not in lines:
                    continue
                if a not in lines:
                    break
                bh = segment_to_hesse_normal_form(b)
                if bh is None:
                    lines.remove(b)
                    continue
                d = avg_line_distance(img.shape, ah, bh)
                if (d < 70):
                    found = True
                    c = [ (a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2, (a[3]+b[3])/2 ]
                    lines.remove(a)
                    lines.remove(b)
                    lines.append(c)

    lines = np.float32(lines)
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
        if l1 is not None and l2 is not None:
            p1 = intersection_point(l1, h)
            p2 = intersection_point(l2, h)
            if p1 is not None and p2 is not None:
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
    return img

def draw_segments(img, segments):
    if len(img.shape) != 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    try:
        for line in segments:
            img = cv2.line(img, (line[0], line[1]), (line[2], line[3]), (255,0,0), 2)
    except KeyError:
        pass
    return img

def get_offset(shape, center):
    global mqttc
    global DEVICE_ID

    c = img.shape[1]//2
    x = center[0]
    mqttc.publish("%s/telemetry/vision/center_offset" % DEVICE_ID, c-x)


def draw_it(result, lane):
    base = result["original"]
    if len(base.shape) != 3:
        base = cv2.cvtColor(base, cv2.COLOR_GRAY2RGB)
    try:
        base = draw_segments(base, result["segments"])
    except KeyError:
        pass
    try:
        for line in result["clustered_lines"][2:]:
            p1 = (line[0], line[1])
            p2 = (line[2], line[3])
            base = cv2.line(base, p1, p2, (0,0,155), 2)
        for line in lane:
            p1 = (line[0], line[1])
            p2 = (line[2], line[3])
            base = cv2.line(base, p1, p2, (0,255,0), 2)
    except KeyError:
        pass
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
        pass
    return base

yoff = 0
def estimate_speed(prev, cur):
    global yoff
    global mqttc
    global DEVICE_ID
    # Convert images to grayscale
    s = (64, 48)
    im1_gray = cv2.resize(cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY), s)
    im2_gray = cv2.resize(cv2.cvtColor(cur,cv2.COLOR_BGR2GRAY), s)
     
    # Find size of image1
    sz = im1_gray.shape
     
    # Define the motion model
    #warp_mode = cv2.MOTION_AFFINE
    warp_mode = cv2.MOTION_TRANSLATION
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    number_of_iterations = 2;
    criteria = (cv2.TERM_CRITERIA_COUNT, number_of_iterations, 0)
    try:
        (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria)
    except cv2.error:
        return
     
    s = math.sqrt(math.pow(warp_matrix[0][2], 2) + math.pow(warp_matrix[1][2], 2))
    lpf = 0.8
    yoff = lpf*yoff + (1-lpf)*s
    mqttc.publish("%s/telemetry/vision/speed" % DEVICE_ID, yoff)

w = int(sys.argv[2])
h = int(sys.argv[3])

cap = cv2.VideoCapture('tcp://0.0.0.0:6000?listen&recv_buffer_size=1024')
if not cap.isOpened():
    raise Exception("Couldn't open cam!")

rv, img = cap.read()
sys.stderr.write("Frame size: %dx%d\n" % (img.shape[1], img.shape[0]))
sys.stderr.write("Resize to: %dx%d\n" % (w,h))
prevFrame = None
l1 = [0,0,0,0]
l2 = [0,0,0,0]
while True:
    rv, img = cap.read()
    if img is None:
        break

    img = cv2.resize(img, (w, h))

    result = detect_lane(img)
    try:
        if len(result["clustered_lines"]) > 1:
            s = 0.8
            la = result["clustered_lines"][0]
            lb = result["clustered_lines"][1]
            if (la[0] > lb[0]):
                la = result["clustered_lines"][1]
                lb = result["clustered_lines"][0]
            l1 = [ int(s*l1[i]+(1-s)*la[i]) for i in range(4) ]
            l2 = [ int(s*l2[i]+(1-s)*lb[i]) for i in range(4) ]
    except KeyError:
        pass
    if OUTPUT_MODE == "original":
        img = result["original"]
    elif OUTPUT_MODE == "mask":
        img = result["mask"]
    elif OUTPUT_MODE == "masked":
        img = result["masked"]
    elif OUTPUT_MODE == "canny":
        img = result["canny"]
    elif OUTPUT_MODE == "hough":
        try:
            img = draw_segments(result["canny"], result["segments"])
        except KeyError:
            img = result["canny"]
    else:
        img = draw_it(result, (l1,l2))
    try:
        get_offset(img.shape, result["center"])
    except KeyError:
        pass
    if len(img.shape) != 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if sys.stdout.isatty():
        cv2.imshow('image', img)
    else:
        sys.stdout.buffer.write(img.tostring())
    if prevFrame is not None and False:
        estimate_speed(prevFrame, result["original"])
    prevFrame = result["original"]
    if chr(cv2.waitKey(1)) == 'q':
        break

cv2.destroyAllWindows()
