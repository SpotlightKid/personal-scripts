#!/usr/bin/env python3
"""Convert MIDI events from Zoom R8 in USB audio interface / Mackie controller
mode into JACK transport commands.
"""

import sys
import time
import jack


MIDI_NOTE_ON = 0x90
MIDI_NOTE_PUNCH_IN = 95


def main(args=None):
    client = jack.Client("zoom2transport")
    midi_in = client.midi_inports.register("midi_in")

    @client.set_process_callback
    def process(frames):
        for offset, data in midi_in.incoming_midi_events():
            status, note, vel = bytes(data)
            ch = status & 0xF
            if status & 0xF0 == MIDI_NOTE_ON and ch == 0:
                if note == MIDI_NOTE_PUNCH_IN:
                    transport = client.transport_query_struct()[0]

                    if transport == jack.STOPPED:
                        print("**Starting** JACK transport", file=sys.stderr)
                        client.transport_start()
                    elif transport == jack.ROLLING:
                        print("**Stopping** JACK transport", file=sys.stderr)
                        client.transport_stop()

    with client:
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("Bye.")
                break


if __name__ == '__main__':
    main()
