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
HOUGH_INTERSECTIONS=20
HOUGH_MIN_LENGTH=30
HOUGH_MAX_GAP=100
# possible: mask, masked, canny, hough, final
OUTPUT_MODE="final"

mqttc = mqtt.Client()
mqttc.connect("127.0.0.1", port=1883)
mqttc.loop_start()
topic = "%s/setconf/vision/#" % DEVICE_ID
print(topic)
mqttc.subscribe(topic)

def on_message(client, userdata, message):
    global CANNY_LOW_THRESHOLD
    global CANNY_HIGH_THRESHOLD
    global OUTPUT_MODE
    global HOUGH_MAX_GAP
    global HOUGH_MIN_LENGTH
    global HOUGH_INTERSECTIONS

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

    sys.stderr.write("Unhandled MQTT topic: %s\n" % topic.join("/"))

mqttc.on_message = on_message

def dump_conf(mqttc):
    global CANNY_LOW_THRESHOLD
    global CANNY_HIGH_THRESHOLD
    global OUTPUT_MODE
    global HOUGH_MAX_GAP
    global HOUGH_MIN_LENGTH
    global HOUGH_INTERSECTIONS
    global DEVICE_ID

    prefix = "%s/conf/vision" % DEVICE_ID
    while True:
        mqttc.publish("%s/canny/low" % prefix, CANNY_LOW_THRESHOLD)
        mqttc.publish("%s/canny/high" % prefix, CANNY_HIGH_THRESHOLD)
        mqttc.publish("%s/hough/max_gap" % prefix, HOUGH_MAX_GAP)
        mqttc.publish("%s/hough/intersections" % prefix, HOUGH_INTERSECTIONS)
        mqttc.publish("%s/hough/min_length" % prefix, HOUGH_MIN_LENGTH)
        mqttc.publish("%s/output_mode" % prefix, OUTPUT_MODE)
        time.sleep(1)

Thread(target=dump_conf, args=(mqttc,)).start()


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

    if OUTPUT_MODE == "mask":
        return None, mask # show just mask
    if OUTPUT_MODE == "masked":
        return None, cv2.bitwise_and(img, mask) # show masked image

    img = cv2.Canny(img, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD)
    if OUTPUT_MODE == "canny":
        return None, img # show canny result
    img = cv2.bitwise_and(img, mask)
    line_segments = cv2.HoughLinesP(img, 1, math.pi/180, HOUGH_INTERSECTIONS, np.array([]), minLineLength=HOUGH_MIN_LENGTH, maxLineGap=HOUGH_MAX_GAP)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if line_segments is None:
        print("Frame skip - no line segments from HoughLines")
        return None, img

    for line in line_segments:
        line = line[0]
        img = cv2.line(img, (line[0], line[1]), (line[2], line[3]), (255,0,0), 2)
    if OUTPUT_MODE == "hough":
        return None, img # show segments

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

w = int(sys.argv[2])
h = int(sys.argv[3])

cap = cv2.VideoCapture('tcp://0.0.0.0:6000?listen&recv_buffer_size=1024')
if not cap.isOpened():
    raise Exception("Couldn't open cam!")

rv, img = cap.read()
sys.stderr.write("Frame size: %dx%d\n" % (img.shape[1], img.shape[0]))
sys.stderr.write("Resize to: %dx%d\n" % (w,h))
while True:
    rv, img = cap.read()
    if not rv:
        time.sleep(0.01)
        continue

    img = cv2.resize(img, (w, h))

    lines, debug = detect_lane(img)
    if lines:
        img = draw_lines(img, lines)
    else:
        img = debug
    if img is not None:
        if len(img.shape) != 3:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        if sys.stdout.isatty():
            cv2.imshow('image', img)
        else:
            sys.stdout.buffer.write(img.tostring())
    if chr(cv2.waitKey(1)) == 'q':
        break

cv2.destroyAllWindows()
