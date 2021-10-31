#!/usr/bin/env python
"""Stream video from a USB-connected DSLR camera supported by gphoto2 to a V4L2 loopback device.

To enable loading the neccessary kernel modules, put the following into
/etc/modprobe.d/dslr-webcam.conf:

    # Module options for Video4Linux, needed for our DSLR Webcam

    alias dslr-webcam v4l2loopback
    options v4l2loopback exclusive_caps=1 max_buffers=2

"""

import argparse
import logging
import sys
from subprocess import PIPE, Popen, run

log = logging.getLogger("dslr-webcam")


GPHOTO_CMD = [
    "gphoto2",
    "--stdout",
    "--capture-movie"
]
FFMPEG_OPTIONS = [
    ("i", "-"),
    ("vcodec", "rawvideo"),
    ("pix_fmt", "yuv420p"),
    ("vf", None),
    ("threads", "0"),
    ("f", "v4l2"),
]
GSTREAMER_PIPELINE = [
    ("fdsrc", {"fd": 0}),
    ("decodebin", {"name": "dec"}),
    ("queue", {}),
    ("videoflip", {"method": "none"}),
    ("videoconvert", {}),
    ("tee", {}),
    ("v4l2sink", {}),
]


def check_v4l2loopback_module():
    proc = run(["lsmod"], capture_output=True, env={"LC_ALL": "C"})
    for line in proc.stdout.decode().splitlines():
        if line.split()[0] == "v4l2loopback":
            return True
    return False


def load_v4l2loopback_module():
    proc = run(["sudo", "-A", "modprobe", "dslr-webcam"])
    if proc.returncode != 0:
        raise RuntimeError("Could not load v4l2loopback module.")


def build_ffmpeg_cmdline(device, flip=None):
    cmd = ["ffmpeg"]
    for opt, arg in FFMPEG_OPTIONS:
        if opt == "vf":
            if flip is None:
                continue
            else:
                arg = flip

        cmd.append("-" + opt)
        cmd.append(arg)

    cmd.append(device)
    return cmd

def build_gstreamer_cmdline(device, flip=None):
    cmd = ["gst-launch-1.0"]
    for mod, opts in GSTREAMER_PIPELINE:
        if mod == "videoflip":
            if flip is None:
                continue
            else:
                opts["method"] = flip

        if mod == "v4l2sink":
            opts["device"] = device

        cmd.append(mod)
        for k,v in opts.items():
            cmd.append("{}={}".format(k, v))

        if mod != "v4l2sink":
            cmd.append("!")

    return cmd


def main(args=None):
    ap = argparse.ArgumentParser(usage=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true", help="Be more verbose.")
    ap.add_argument(
        "-f",
        "--flip",
        choices=["h", "horizontal", "v", "vertical"],
        help="Flip video output horizontally or vertically.",
    )
    ap.add_argument(
        "-m",
        "--method",
        choices=["f", "ffmpeg", "g", "gst", "gstreamer"],
        default="gstreamer",
        help="Video output conversion method (default: %(default)s)",
    )
    ap.add_argument(
        "-d",
        "--device",
        default="/dev/video0",
        help="V4L2 device (default: %(default)s)"
    )
    args = ap.parse_args(args)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(name)s] %(levelname)s: %(message)s",
    )

    if not check_v4l2loopback_module():
        if args.verbose:
            print("Loading v4l2loopback module...", file=sys.stderr)
        load_v4l2loopback_module()

    device = args.device

    if device.isnumeric():
        device = "/dev/video{}".format(device)

    if args.method in ("f", "ffmpeg"):
        if args.flip in ("h", "horizontal"):
            flip = "hflip"
        elif args.flip in ("v", "vertical"):
            flip = "vflip"
        else:
            flip = None

        conv_cmd = build_ffmpeg_cmdline(device, flip)
    elif args.method in ("g", "gst", "gstreamer"):
        if args.flip in ("h", "horizontal"):
            flip = "horizontal-flip"
        elif args.flip in ("v", "vertical"):
            flip = "vertical-flip"
        else:
            flip = None

        conv_cmd = build_gstreamer_cmdline(device, flip)

        if not args.verbose:
            conv_cmd.insert(1, "-q")

    log.debug("Conversion command: %r", conv_cmd)
    capture_proc = Popen(GPHOTO_CMD, stdout=PIPE)
    conv_proc = Popen(conv_cmd, stdin=capture_proc.stdout)
    capture_proc.stdout.close()

    try:
        conv_proc.communicate()
    except KeyboardInterrupt:
        pass
    finally:
        if capture_proc.returncode is None:
            capture_proc.terminate()
        if conv_proc.returncode is None:
            conv.terminate()


if __name__ == "__main__":
    sys.exit(main() or 0)
