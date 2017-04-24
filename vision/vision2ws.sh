#!/bin/bash
W=$2
H=$3
set -x
python3 vision.py "$@" | ffmpeg -f rawvideo -pixel_format bgr24 -framerate 60 -video_size "$W"x"$H" -i - -b:v 10000000 -f mpeg1video http://127.0.0.1:8082/$W/$H/ 2>/dev/null
