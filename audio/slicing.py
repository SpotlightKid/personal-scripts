"""Utility routine to slice sound files at given timestamps"""

import os
from aubio import source, sink


def slice_source_at_stamps(
    source_file,
    regions,
    samplerate=0,
    hop_size=256,
    output_dir=None,
    exist_ok=True,
    output_template="{basename}_{slice:02}.{ext}",
    verbose=False,
):
    """Slice a sound file at given timestamps.

    This function reads `source_file` and creates slices, new smaller
    files each starting at `t[0]` in `regions`, a list of (start, end)
    integer tuples corresponding to time locations in `source_file`,
    in sample frames.

    If `output_dir` is unspecified, the new slices will be written in
    the current directory. If `output_dir` is a string, new slices
    will be written in `output_dir`, after creating the directory if
    required.

    The default `samplerate` is 0, meaning the original sampling rate
    of `source_file` will be used. When using a sampling rate
    different to the one of the original files, `timestamps` and
    `timestamps_end` should be expressed in the re-sampled signal.

    The `hop_size` parameter simply tells :class:`source` to use this
    hop size and does not change the output slices.

    If `add_first` is True and `timestamps` does not start with `0`, the
    first slice from `0` to `timestamps[0] - 1` will be automatically added.

    Parameters
    ----------
    source_file : str
        path of the resource to slice
    regions : :obj:`list` of :obj:`tuple[int, int]`
        time stamps at which to slice, in sample frames
    output_dir : str (optional)
        output directory to write the slices to
    samplerate : int (optional)
        samplerate to read the file at
    hop_size : int (optional)
        number of samples read from source per iteration
    add_first : bool (optional)
        always create the slice at the start of the file

    Examples
    --------

    Create two slices: the first slice starts at the beginning of the
    input file `loop.wav` and lasts exactly one second, starting at
    sample `0` and ending at sample `44099`; the second slice starts
    at sample `44100` and lasts until the end of the input file:

    >>> aubio.slice_source_at_stamps('loop.wav', [(0, 44100), (44100, None]])

    Create one slice, from 1 second to 2 seconds:

    >>> aubio.slice_source_at_stamps('loop.wav', [(44100, 44100 * 2 - 1)])

    Notes
    -----

    Slices may be overlapping.

    """
    if not regions:
        raise ValueError("No regions timestamps given")

    source_base_name, _ = os.path.splitext(os.path.basename(source_file))

    if output_dir is None:
        output_dir = os.path.basename(source_file)

    os.makedirs(output_dir, exist_ok=exist_ok)

    def _new_sink_name(slice_, basename, timestamp, samplerate):
        # create name based on a output_template
        timestamp_seconds = timestamp / float(samplerate)
        return os.path.join(
            output_dir,
            output_template.format(
                basename=basename,
                timestamp_seconds="%011.6f" % timestamp_seconds,
                ext="wav",
                timestamp=timestamp,
                slice=slice_,
                samplerate=samplerate,
            ),
        )

    # open source file
    _source = source(source_file, samplerate, hop_size)
    samplerate = _source.samplerate

    total_frames = 0
    slices = []
    slice_ = 0

    while True:
        # get hop_size new samples from source
        vec, read = _source.do_multi()
        # if the total number of frames read will exceed the next region start
        while regions and total_frames + read >= regions[0][0]:
            # get next region
            start_stamp, end_stamp = regions.pop(0)
            slice_ += 1
            # create a name for the sink
            new_sink_path = _new_sink_name(slice_, source_base_name, start_stamp, samplerate)
            # create its sink
            _sink = sink(new_sink_path, samplerate, _source.channels)
            # create a dictionary containing all this
            new_slice = {"start_stamp": start_stamp, "end_stamp": end_stamp, "sink": _sink}
            # append the dictionary to the current list of slices
            slices.append(new_slice)

            if verbose:
                print(f"Writing slice #{slice_} to '{_sink.uri}'.")

        for i, current_slice in enumerate(slices):
            start_stamp = current_slice["start_stamp"]
            end_stamp = current_slice["end_stamp"]
            _sink = current_slice["sink"]
            # sample index to start writing from new source vector
            start = max(start_stamp - total_frames, 0)
            # number of samples yet to written be until end of region
            remaining = end_stamp - total_frames + 1

            # not enough frames remaining, time to split
            if remaining < read:
                if remaining > start:
                    # write remaining samples from current region
                    _sink.do_multi(vec[:, start:remaining], remaining - start)
                    # close this file
                    _sink.close()
            elif read > start:
                # write all the samples
                _sink.do_multi(vec[:, start:read], read - start)

        total_frames += read
        # remove old slices
        slices = list(filter(lambda s: s["end_stamp"] > total_frames, slices))

        if read < hop_size:
            break
