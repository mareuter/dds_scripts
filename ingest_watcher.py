import argparse
from datetime import datetime
import logging
import os
import subprocess

import pyinotify

ACCS_IMAGE_DIR = '/mnt/data/ats/mcm'
ATA_IMAGE_DIR = '/mnt/data/export'

ACCS_INGEST_DIR = '/home/lsst/ingest/accs'
ATA_INGEST_DIR = '/home/lsst/ingest/dmcs'

INGEST_CMD = 'ingestImages.py'


class EventHandlerTest(pyinotify.ProcessEvent):

    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname
        print(f'WRITE: {path}')
        cmd = ['python', 'process_file.py', path]
        subprocess.run(cmd)

class EventHandler(pyinotify.ProcessEvent):

    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname
        if 'fits' in path:
            print(f'WRITE: {path}')
            cmd = [INGEST_CMD]
            if ACCS_IMAGE_DIR in path:
                cmd.append(ACCS_INGEST_DIR)
            if ATA_IMAGE_DIR in path:
                cmd.append(ATA_IMAGE_DIR)
            cmd.append(path)
            subprocess.run(cmd)

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run the program in test mode.')
    parser.add_argument('-d', '--dir', help='Directory to monitor. Only used in test mode.')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    if args.test and args.dir is None:
            parser.error('Need to set a directory in test mode.')

    fmt = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = f'ingest_watcher_{fmt}.log'
    #print(logfile)

    mask = pyinotify.IN_CLOSE_WRITE

    wm = pyinotify.WatchManager()

    if args.test:
        handler = EventHandlerTest()
    else:
        handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)

    if args.test:
        wm.add_watch(args.dir, mask, rec=True, auto_add=True)
    else:
        wm.add_watch([ACCS_IMAGE_DIR, ATA_IMAGE_DIR],
                     mask, rec=True, auto_add=True)
    notifier.loop()
