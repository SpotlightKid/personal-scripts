#!/usr/bin/env python3
"""Slice audio file with recording of samples separated by silence via aubio."""

import argparse
import sys
from pathlib import Path

import aubio

from slicing import slice_source_at_stamps

PROG = "slicesamples"


def main(args=None):
    ap = argparse.ArgumentParser(prog=PROG, description=__doc__.splitlines()[0])
    ap.add_argument(
        "-o", "--output-dir", metavar="DIR", help="Output directory (default: same as input file)"
    )
    ap.add_argument(
        "-f",
        "--output-format",
        default="{basename}_{slice:02}.{ext}",
        metavar="TEMPLATE",
        help="Output filename template (default: %(default)r)",
    )
    ap.add_argument(
        "-O",
        "--onset-method",
        choices=["default", "complexdomain", "hfc", "phase", "specdiff", "energy", "kl", "mkl"],
        default="default",
        metavar="METHOD",
        help=(
            "Onset detection method (default: %(default)s): "
            "complexdomain|hfc|phase|specdiff|energy|kl|mkl"
        ),
    )
    ap.add_argument(
        "-m",
        "--min-interval",
        metavar="INTERVAL",
        default="12ms",
        help="Minimum Inter-Onset Interval (default: %(default)s)",
    )
    ap.add_argument(
        "-M",
        "--min-silent-hops",
        type=int,
        metavar="HOPS",
        default=10,
        help="Minimum number of hop periods under threshold to start silence period (default: %(default)i)",
    )
    ap.add_argument(
        "-t",
        "--onset-threshold",
        metavar="VAL",
        default=0.3,
        help="Onset peak picking threshold (default: %(default).1f)",
    )
    ap.add_argument(
        "-s",
        "--silence-threshold",
        type=float,
        metavar="dbFS",
        default=-70.0,
        help="Silence threshold in dbFS (default: %(default).2f)",
    )
    ap.add_argument(
        "-H",
        "--hop-size",
        type=int,
        metavar="FRAMES",
        default=256,
        help="Hop size in sample frames (default: %(default)i)",
    )
    ap.add_argument("-v", "--verbose", action="store_true", help="Be more verbose.")
    ap.add_argument(dest="input_file", help="Input audio file.")

    args = ap.parse_args(args)

    with aubio.source(args.input_file, hop_size=args.hop_size) as audio_source:
        nframes = 0
        nhops = 0
        onsets = 0
        read = 0
        sections = []
        silence_start = -1
        silence_end = -1
        signal_start = -1

        onset = aubio.onset(
            args.onset_method,
            buf_size=512,
            hop_size=args.hop_size,
            samplerate=audio_source.samplerate,
        )

        if args.min_interval:
            if args.min_interval.endswith("ms"):
                onset.set_minioi_ms(int(args.min_interval[:-2]))
            elif args.min_interval.endswith("s"):
                onset.set_minioi_s(int(args.min_interval[:-1]))
            else:
                onset.set_minioi(int(args.min_interval))

        onset.set_threshold(args.onset_threshold)

        if args.verbose:
            print(f"Analyzing file '{args.input_file}'...")

        while True:
            frames, read = audio_source()

            if onset(frames):
                onset_frame = onset.get_last()
                onsets += 1

                if args.verbose:
                    print(f"Onset #{onsets:02} detected at: {onset.get_last_s():.4f}")

                if signal_start != -1:
                    if silence_start != -1 and silent_hops >= args.min_silent_hops:
                        sections.append((signal_start, silence_start - 1))
                    else:
                        sections.append((signal_start, onset_frame - 1))

                signal_start = onset_frame
                silence_start = -1
                silent_hops = 0
            elif signal_start != -1:
                if aubio.silence_detection(frames, args.silence_threshold):
                    if silence_start == -1:
                        silence_start = nframes

                    silent_hops += 1

            nframes += read
            nhops += 1

            if read < audio_source.hop_size:
                break

        if signal_start != -1:
            if silence_start != -1 and silent_hops >= args.min_silent_hops:
                sections.append((signal_start, silence_start - 1))
            else:
                sections.append((signal_start, nframes - 1))

        if args.verbose:
            print(f"Read frames={nframes}, hops={nhops}, hop_size={args.hop_size}")

        if sections:
            slice_source_at_stamps(
                args.input_file,
                sections,
                hop_size=args.hop_size,
                output_dir=args.output_dir,
                output_template=args.output_format,
                verbose=args.verbose,
            )


if __name__ == "__main__":
    sys.exit(main() or 0)
