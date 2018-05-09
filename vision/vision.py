import sys
import numpy as np
import math
import gzip
import time
import tensorflow as tf
from object_detection.utils import label_map_util, visualization_utils
import os
import cv2
import paho.mqtt.client as mqtt
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from utils import *

# must be odd number:
MAX_CLASSES=90
DEVICE_ID=sys.argv[1]
MY_IP=sys.argv[4]
MQTT_IP=sys.argv[5]
VIDEO_PORT=int(os.getenv("VIDEO_PORT", 7000))
VIDEO_PROTO=os.getenv("VIDEO_PROTO", "tcp")
HTTP_PORT=int(os.getenv("HTTP_PORT", 8089))
CANNY_LOW_THRESHOLD=150
CANNY_HIGH_THRESHOLD=200
HOUGH_INTERSECTIONS=20
HOUGH_MIN_LENGTH=100
HOUGH_MAX_GAP=40
# possible: mask, masked, canny, hough, final
OUTPUT_MODE="final"
LANE_DETECT_HEIGHT=150
LINE_MERGE_DISTANCE=0
LINE_SMOOTHING=0.1


class ObjectDetectionPredict():
    def __init__(self, model_path, labels_path):
        label_map = label_map_util.load_labelmap(labels_path)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=MAX_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        self.load_tf_graph(model_path)

    def load_tf_graph(self, model_path):
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(model_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=self.detection_graph)
        return 0


    def detect_objects(self, image_np):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

        # Each box represents a part of the image where a particular object was detected.
        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represent the level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        # Actual detection.
        (boxes, scores, classes, num_detections) = self.sess.run(
            [boxes, scores, classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})

        # Visualization of the results of a detection.
        visualization_utils.visualize_boxes_and_labels_on_image_array(
            image_np,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8)
        return scores, classes, image_np

class Stream(BaseHTTPRequestHandler):
    img = None
    raw_img = None
    predictor = ObjectDetectionPredict("./frozen_inference_graph.pb", "./label_map.pbtxt")
    protocol_version = 'HTTP/1.1'
    def log_message(self, format, *args):
        return
    def do_GET(self):
        if Stream.img is None or Stream.raw_img is None:
            self.send_response(404)
            self.send_header("Content-Length", 0)
            self.end_headers()
            return
        try:
            self.path.index("objects")
            scores, classes, img = Stream.predictor.detect_objects(Stream.raw_img)
        except ValueError:
            img = Stream.img
        content = cv2.imencode('.jpg', img, (50,))[1].tostring()
        self.send_response(200)
        self.send_header("Content-Length", len(content))
        self.send_header('Content-Type','image/jpg')
        self.end_headers()
        self.wfile.write(content)
        self.wfile.flush()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def http_start():
    global HTTP_PORT
    server_address = ('0.0.0.0', HTTP_PORT)
    httpd = ThreadedHTTPServer(server_address, Stream)
    httpd.serve_forever()

Thread(target=http_start).start()

mqttc = mqtt.Client()

def on_message(client, userdata, message):
    global CANNY_LOW_THRESHOLD
    global CANNY_HIGH_THRESHOLD
    global OUTPUT_MODE
    global HOUGH_MAX_GAP
    global HOUGH_MIN_LENGTH
    global HOUGH_INTERSECTIONS
    global LANE_DETECT_HEIGHT
    global LINE_MERGE_DISTANCE
    global LINE_SMOOTHING

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
    elif topic[0] == "line_merge_distance":
        LINE_MERGE_DISTANCE = int(message.payload)
        sys.stderr.write("LINE_MERGE_DISTANCE=%d\n" % LINE_MERGE_DISTANCE)
        return
    elif topic[0] == "line_smoothing":
        LINE_SMOOTHING = float(message.payload)
        sys.stderr.write("LINE_SMOOTHING=%f\n" % LINE_SMOOTHING)
        return
    sys.stderr.write("Unhandled MQTT topic: %s\n" % "/".join(topic))

def on_connect(client, userdata, flags, rc):
    topic = "%s/setconf/vision/#" % DEVICE_ID
    client.subscribe(topic)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.connect_async(MQTT_IP, port=1883)
mqttc.loop_start()

def dump_conf(mqttc):
    prefix = "%s/conf/vision" % DEVICE_ID
    while True:
        mqttc.publish("%s/camera_stream/0" % DEVICE_ID, "http://%s:%s" % (MY_IP, HTTP_PORT))
        mqttc.publish("%s/camera_stream/0/objects" % DEVICE_ID, "http://%s:%s/objects" % (MY_IP, HTTP_PORT))
        mqttc.publish("%s/canny/low" % prefix, CANNY_LOW_THRESHOLD)
        mqttc.publish("%s/canny/high" % prefix, CANNY_HIGH_THRESHOLD)
        mqttc.publish("%s/hough/max_gap" % prefix, HOUGH_MAX_GAP)
        mqttc.publish("%s/hough/intersections" % prefix, HOUGH_INTERSECTIONS)
        mqttc.publish("%s/hough/min_length" % prefix, HOUGH_MIN_LENGTH)
        mqttc.publish("%s/output_mode" % prefix, OUTPUT_MODE)
        mqttc.publish("%s/lane_detect_height" % prefix, LANE_DETECT_HEIGHT)
        mqttc.publish("%s/line_merge_distance" % prefix, LINE_MERGE_DISTANCE)
        mqttc.publish("%s/line_smoothing" % prefix, LINE_SMOOTHING)
        time.sleep(1)

Thread(target=dump_conf, args=(mqttc,)).start()

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
        k = min(2, len(lines))
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
                if (d < LINE_MERGE_DISTANCE):
                    found = True
                    c = merge_lines(a,b)
                    lines.remove(a)
                    lines.remove(b)
                    lines.append(c)

    lines = np.float32(lines)
    # we prefer vertical lines
    lines = sorted(lines, key=lambda l: abs(l[0] - l[2]))
    result["clustered_lines"] = lines
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
    base = result["original"].copy()
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

def find_center(result, l1, l2):
    h = (0,1,-LANE_DETECT_HEIGHT)
    if l1[0] > l2[0]:
        t = l1
        l1 = l2
        l2 = t

    l1 = segment_to_hesse_normal_form(l1)
    l2 = segment_to_hesse_normal_form(l2)
    if l1 is not None and l2 is not None:
        p1 = intersection_point(l1, h)
        p2 = intersection_point(l2, h)
        if p1 is not None and p2 is not None:
            result["intersections"] = ( p1,p2, line_to_points(h, result["original"].shape))
            result["center"] = ((p1[0] + p2[0])//2, (p1[1] + p2[1])//2)
    return result

w = int(sys.argv[2])
h = int(sys.argv[3])

cap = cv2.VideoCapture('%s://0.0.0.0:%s?listen' % (VIDEO_PROTO, VIDEO_PORT))
if not cap.isOpened():
    raise Exception("Couldn't open cam!")

rv, img = cap.read()
sys.stderr.write("Frame size: %dx%d\n" % (img.shape[1], img.shape[0]))
sys.stderr.write("Resize to: %dx%d\n" % (w,h))
prevFrame = None
l1 = [0,0,0,0]
l2 = [0,0,0,0]
t = Thread()
tfps = 0
pfps = 0
trshape = None
writer = cv2.VideoWriter("out.avi", cv2.VideoWriter_fourcc(*'XVID'), 60, (img.shape[1], img.shape[0]))
while True:
    tstart = time.time()
    while time.time() - tstart < 0.01:
        tstart = time.time()
        rv, img = cap.read()
    pstart = time.time()
    if img is None:
        break

    img = cv2.resize(img, (w, h))

    result = detect_lane(img)
    try:
        if len(result["clustered_lines"]) > 1:
            la = result["clustered_lines"][0]
            lb = result["clustered_lines"][1]
            if (la[0] > lb[0]):
                la = result["clustered_lines"][1]
                lb = result["clustered_lines"][0]
            l1 = merge_lines(l1, la, LINE_SMOOTHING)
            l2 = merge_lines(l2, lb, LINE_SMOOTHING)
    except KeyError:
        pass
    result = find_center(result, l1, l2)
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
    Stream.img = img
    Stream.raw_img = result["original"]
    writer.write(img)
    if prevFrame is not None and not t.is_alive():
        t = Thread(target=estimate_speed, args=(prevFrame, result["original"]))
        t.start()
    prevFrame = result["original"]
    #if sys.stdout.isatty():
    #    if chr(cv2.waitKey(1)) == 'q':
    #        break
    tfps = 0.9*tfps + 0.1/(time.time() - tstart)
    pfps = 0.9*pfps + 0.1/(time.time() - pstart)
    mqttc.publish("%s/telemetry/vision/fps" % DEVICE_ID, int(tfps))
    mqttc.publish("%s/telemetry/vision/processing_fps" % DEVICE_ID, int(pfps))

cv2.destroyAllWindows()
