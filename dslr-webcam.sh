#!/bin/bash
#
# dslr-webcam - stream video from a USB-connected DSLR supported by gphoto2
#               to a Video4Linux (V4L) device

# To enable loading the neccessary kernel modules, put the following into
# /etc/modprobe.d/dslr-webcam.conf:
#
#    # Module options for Video4Linux, needed for our DSLR Webcam
#
#    alias dslr-webcam v4l2loopback
#    options v4l2loopback exclusive_caps=1 max_buffers=2

if ! lsmod | grep -q v4l2loopback; then
    sudo modprobe dslr-webcam
fi

case "$1" in
    f|ffmpeg)
        METHOD="ffmeg"
        ;;
    g|gst|gstreamer)
        METHOD="gstreamer"
        ;;
    *)
        METHOD="gstreamer"
        ;;
esac

if [[ "$METHOD" = "ffmpeg" ]]; then
    exec gphoto2 \
            --stdout \
            --capture-movie | \
        ffmpeg -i - \
            -vcodec rawvideo \
            -pix_fmt yuv420p \
            -threads 0 \
            -f v4l2 \
            ${DEVICE:-/dev/video0}
elif [[ "$METHOD" = "gstreamer" ]]; then
    exec gphoto2 \
            --stdout \
            --capture-movie | \
        gst-launch-1.0 \
            fdsrc fd=0 ! \
            decodebin name=dec ! \
            queue ! \
            videoconvert ! \
            tee ! \
            v4l2sink device=${DEVICE:-/dev/video0}
else
    echo "Unsupported video conversion method $METHOD." >/dev/stderr
    exit 1
fi
