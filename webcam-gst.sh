#!/bin/bash
#
# webcam-gst - show video from V4L2 cam with GStreamer
#

exec gst-launch-1.0 v4l2src device=${1:-/dev/video0} ! autovideosink
