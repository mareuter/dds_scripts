import argparse
import logging
import logging.handlers
import os
import subprocess

import pyinotify

LOG_NAME = "ingest_watcher"
LOG_FILE_SIZE = 1000000  # 1 MB
LOG_FILES_TO_KEEP = 10

ACCS_IMAGE_DIR = '/mnt/data/ats/mcm'
ATA_IMAGE_DIR = '/mnt/dmcs'

ACCS_INGEST_DIR = '/home/lsst/ingest/accs'
ATA_INGEST_DIR = '/home/lsst/ingest/dmcs'

INGEST_CMD = 'ingestImages.py'


class EventHandlerTest(pyinotify.ProcessEvent):

    logger = logging.getLogger(LOG_NAME)

    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname
        self.logger.info(f'WRITE: {path}')
        cmd = ['python', 'process_file.py', path]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True)
        for line in proc.stdout.split(os.linesep):
            if line != '':
                self.logger.info(line)

    def process_IN_CLOSE_NOWRITE(self, event):
        self.logger.info(f'NOWRITE: {event.pathname}')

class EventHandler(pyinotify.ProcessEvent):

    logger = logging.getLogger(LOG_NAME)

    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname
        if 'fits' in path:
            self.logger.info(f'WRITE: {path}')
            cmd = [INGEST_CMD]
            if ACCS_IMAGE_DIR in path:
                cmd.append(ACCS_INGEST_DIR)
            if ATA_IMAGE_DIR in path:
                cmd.append(ATA_IMAGE_DIR)
            cmd.append(path)
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True)
            for line in proc.stdout.split(os.linesep):
                if line != '':
                    self.logger.info(line)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run the program in test mode.')
    parser.add_argument('-d', '--dir', help='Directory to monitor. Only used in test mode.')
    return parser

def setup_logger():
    logfile = 'ingest_watcher.log'
    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    rfh = logging.handlers.RotatingFileHandler(logfile, maxBytes=LOG_FILE_SIZE,
                                               backupCount=LOG_FILES_TO_KEEP)
    rfh.setFormatter(formatter)
    logger.addHandler(rfh)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    if args.test and args.dir is None:
        parser.error('Need to set a directory in test mode.')

    setup_logger()

    mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CLOSE_NOWRITE

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
