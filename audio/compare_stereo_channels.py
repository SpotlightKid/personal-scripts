#!/usr/bin/env python3
"""Compare stereo audio channels for equality and similarity.

This script:

- Reads an audio file using python-soundfile (libsndfile) for broad format support.
- Determines if the file is stereo.
- If stereo, compares left and right channels:
  - Exact/approximate sample-by-sample equality.
  - Optional "invert-sum similarity" check: compute residual = left + (-right),
    then evaluate whether the residual exceeds a threshold.

The invert-sum check is useful for detecting near-identical channels even if small
differences exist (e.g., due to dithering or encoding), by measuring how much
cancellation happens when one channel is inverted.

Works in streaming/chunked mode to handle large files efficiently.

Usage:
  compare_stereo_channels.py <audio_file>
    [--threshold 0.0]
    [--dtype float64]
    [--chunk-frames 262144]
    [--isr]
    [--rms]
    [--relative]

Examples:
  compare_stereo_channels.py song.wav
  compare_stereo_channels.py track.flac --threshold 1e-7
  compare_stereo_channels.py mix.aiff --dtype int32
  compare_stereo_channels.py stereo.flac --isr --threshold 1e-7
  compare_stereo_channels.py stereo.flac --isr --peak --threshold 1e-4
  compare_stereo_channels.py stereo.flac --isr --relative --threshold 0.01

Interpretation of invert-sum threshold:

- Absolute mode (default): residual metric (RMS or peak) is compared directly to the threshold.
- Relative mode (--relative): compares residual metric relative to the signal magnitude.
  residual_ratio = residual_metric / max(signal_metric, eps)
  The residual_ratio must be <= threshold to be considered "similar".

"""

import argparse
import logging
import sys
from typing import Tuple

import numpy as np
import soundfile as sf


log = logging.getLogger("compare_stereo")


def parse_args(args=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Determine if an audio file is stereo and whether both channels contain identical or similar audio."
    )
    parser.add_argument(
        "audio_file",
        help="Path to the audio file (any format supported by libsndfile/soundfile).",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.0,
        help=(
            "Sample / residual value difference threshold (default 0.0). "
            "Use 0.0 for exact equality. A small positive value (e.g., 1e-8) "
            "can account for float conversions."
        ),
    )
    parser.add_argument(
        "-s",
        "--dtype",
        choices=["float64", "float32", "int32", "int16"],
        default="float64",
        help=(
            "Data type to read samples as. For exact PCM equality, prefer an integer dtype "
            "(e.g. int16 or int32 if supported by the source) (default: float64)."
        ),
    )
    parser.add_argument(
        "-c",
        "--chunk-frames",
        type=int,
        default=262144,
        help="Number of frames to process per chunk (default: 262144).",
    )
    parser.add_argument(
        "-i",
        "--isr",
        action="store_true",
        help=(
            "Enable invert-sum residual check: "
            "disabled (default): compare if sample frames are equal or difference <= threshold."
            "enabled: compare if residual signal (L - R) is within threshold."
        ),
    )
    parser.add_argument(
        "-r",
        "--rms",
        action="store_true",
        help="Use RMS of signal instead of peak value.",
    )
    parser.add_argument(
        "-R",
        "--relative",
        action="store_true",
        help=(
            "Use relative thresholding: residual metric divided by signal metric (RMS or peak of channels) "
            "must be <= threshold. Useful if the signal levels of both channels are different."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity of output (can be given more than once).",
    )
    return parser.parse_args(args)


def channels_equal(f: sf.SoundFile, dtype: str, chunk_frames: int, tol: float) -> Tuple[bool, int]:
    """Read through the file and compare left/right channels.

    Returns:
      (equal, total_frames_compared)

    Comparison uses:
      - exact equality (np.array_equal) for tol == 0
      - np.allclose for tol > 0

    """
    equal = True
    total_frames = 0

    if f.channels != 2:
        raise TypeError("Only audio files with two channels are supported.")

    while True:
        data = f.read(frames=chunk_frames, dtype=dtype, always_2d=True)
        if data.size == 0:
            break

        left = data[:, 0]
        right = data[:, 1]

        total_frames += data.shape[0]

        if tol == 0.0:
            if not np.array_equal(left, right):
                equal = False
                break
        else:
            if not np.allclose(left, right, rtol=1e-12, atol=tol, equal_nan=True):
                equal = False
                break

    return equal, total_frames


def invert_sum_similarity(
    f: sf.SoundFile,
    dtype: str,
    chunk_frames: int,
    rms: bool,
    threshold: float,
    relative: bool,
) -> Tuple[bool, int, float, float]:
    """Check similarity by residual = L - R.

    Accumulates residual metric and signal metric over the whole file in streaming fashion.

    Parameters:
      - mode: 'rms' or 'peak'
      - threshold: numeric threshold for the decision
      - relative: if True, compare residual_metric/signal_metric to threshold; else compare residual_metric to threshold

    Returns:
      (similar, total_frames, residual_metric, signal_metric)

    """
    total_frames = 0

    # Running accumulators for RMS and peak across chunks
    residual_energy = 0.0  # sum of residual^2 for RMS
    signal_energy = 0.0    # sum of signal^2 for RMS baseline (both channels combined)
    residual_peak = 0.0
    signal_peak = 0.0

    if f.channels != 2:
        raise TypeError("Only audio files with two channels are supported.")

    while True:
        data = f.read(frames=chunk_frames, dtype=dtype, always_2d=True)
        if data.size == 0:
            break

        left = data[:, 0]
        right = data[:, 1]
        residual = left - right  # L + (-R)

        # Update frames
        n = data.shape[0]
        total_frames += n

        if rms:
            # Accumulate energy (sum of squares)
            residual_energy += float(np.dot(residual, residual))
            # Use combined channel energy as signal baseline
            signal_energy += float(np.dot(left, left) + np.dot(right, right))
        else:  # peak
            residual_peak = max(residual_peak, float(np.max(np.abs(residual))))
            signal_peak = max(signal_peak, float(max(np.max(np.abs(left)), np.max(np.abs(right)))))

    # Compute metrics
    if rms:
        # Avoid division by zero; if no frames, metrics remain 0
        residual_metric = np.sqrt(residual_energy / max(total_frames, 1))
        signal_metric = np.sqrt(signal_energy / max(total_frames, 1))
    else:
        residual_metric = residual_peak
        signal_metric = signal_peak

    # Decision
    eps = 1e-20
    if relative:
        ratio = residual_metric / max(signal_metric, eps)
        similar = ratio <= threshold
    else:
        similar = residual_metric <= threshold

    return similar, total_frames, residual_metric, signal_metric


def main(args=None) -> int:
    args = parse_args(args)
    
    logging.basicConfig(
        level={1: logging.INFO, 2: logging.DEBUG}.get(args.verbose, logging.WARNING),
        format="%(levelname)s: %(message)s"
    )

    with sf.SoundFile(args.audio_file, mode="r") as f:
        if f.channels != 2:
            log.warning(f"File is not stereo (channels={f.channels}).")
            return 0

        log.debug(f"Samplerate: {f.samplerate} Hz")

        if not args.isr:
            # Equality/approximate equality
            try:
                equal, nframes_equal = channels_equal(
                    f, dtype=args.dtype, chunk_frames=args.chunk_frames, tol=args.threshold
                )
            except Exception as e:
                log.error(f"Error reading or comparing audio: {e}")
                return 2

            log.debug(f"Frames compared (equality): {nframes_equal}")

            log.info(f"Direct sample comparison (tolerance: {args.threshold}): " +
                     ("same audio" if equal else "channels 1 and 2 differ"))
        else:
            # Alternative invert-sum similarity check
            try:
                equal, nframes_sim, residual_metric, signal_metric = invert_sum_similarity(
                    f,
                    dtype=args.dtype,
                    chunk_frames=args.chunk_frames,
                    rms=args.rms,
                    threshold=args.threshold,
                    relative=args.relative,
                )
            except Exception as e:
                log.error(f"Error during invert-sum similarity check: {e}")
                return 2

            log.debug(f"Invert-sum comparison enabled "
                  f"(threshold={args.threshold}, "
                  f"{'relative' if args.relative else 'absolute'}).")
            log.debug(f"Frames compared (invert-sum): {nframes_sim}")

            # Report metrics
            metric_name = "RMS" if args.rms else "Peak"
            log.debug(f"Residual {metric_name}: {residual_metric:.6e}")
            log.debug(f"Signal {metric_name}:   {signal_metric:.6e}")
            
            if args.relative:
                ratio = residual_metric / max(signal_metric, 1e-20)
                log.debug(f"Residual ratio:   {ratio:.6e}")

            log.info("Invert-sum comparison: channels are " +
                ("NOT " if not equal else "") + "similar (residual " +
                ("within" if equal else "exceeds") + f" threshold = {args.threshold}).")

    return 1 if equal else 0


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
