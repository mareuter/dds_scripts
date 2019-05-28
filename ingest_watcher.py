import argparse
import asyncio
from datetime import datetime
import logging
import logging.handlers
import os
import subprocess

LOG_NAME = "ingest_watcher"
LOG_FILE_SIZE = 1000000  # 1 MB
LOG_FILES_TO_KEEP = 10

OUTPUT_FILE_EXT = ".fits"
DATE_DIR_FORMAT = "%Y%m%d"
MAX_DIR_COUNT = 3

ACCS_IMAGE_DIR = '/mnt/data/ats/mcm'
ATA_IMAGE_DIR = '/mnt/dmcs'

ACCS_INGEST_DIR = '/home/lsst/ingest/accs'
ATA_INGEST_DIR = '/home/lsst/ingest/dmcs'

INGEST_CMD = 'ingestImages.py'


class Watcher:

    logger = logging.getLogger(LOG_NAME)

    def __init__(self, input_dir=None, test_mode=False):
        self.test_mode = test_mode
        self.loop = None
        if input_dir is None:
            self.dirs = [ACCS_IMAGE_DIR, ATA_IMAGE_DIR]
        else:
            self.dirs = [input_dir]

        self.date_dirs = []
        self.dir_set = {}
        self.does_date_dir_exist()

    def _get_date_str(self):
        return datetime.utcnow().strftime(DATE_DIR_FORMAT)

    async def check_for_date_dir(self):
        while True:
            self.does_date_dir_exist()
            await asyncio.sleep(30)

    async def check_for_files(self):
        while True:
            for ldir in self.dir_set:
                self.logger.info(f'C: {ldir}')
                cfiles = set([f for f in os.listdir(ldir)
                              if os.path.isfile(os.path.join(ldir, f)) and f.endswith(OUTPUT_FILE_EXT)])

                self.logger.info(f'D: {cfiles}')
                ofiles = self.dir_set[ldir]
                self.logger.info(f'B: {ofiles}')
                if ofiles is not None:
                    nfiles = ofiles.symmetric_difference(cfiles)
                    if len(nfiles):
                        self.dir_set[ldir] = cfiles
                else:
                    nfiles = cfiles
                    self.dir_set[ldir] = nfiles

                self.logger.info(f'A: {nfiles}')
                if len(nfiles):
                    self.process(ldir, nfiles)
            await asyncio.sleep(10)

    def does_date_dir_exist(self):
        date_dir = self._get_date_str()
        self.logger.info(f'H: {date_dir}')
        for ldir in self.dirs:
            full_path = os.path.join(ldir, date_dir)
            if os.path.exists(full_path) and full_path not in self.dir_set:
                self.dir_set[full_path] = None
                if date_dir not in self.date_dirs:
                    self.date_dirs.append(date_dir)
                    self.logger.info(f'K: {self.date_dirs}')
        self.prune_date_dirs()

    def process(self, input_dir, new_files):
        cmds_to_run = []
        if self.test_mode:
            for new_file in new_files:
                cmds_to_run.append(['python', 'process_file.py', os.path.join(input_dir, new_file)])
        else:
            for new_file in new_files:
                cmd = [INGEST_CMD]
                if ACCS_IMAGE_DIR in input_dir:
                    cmd.append(ACCS_INGEST_DIR)
                if ATA_IMAGE_DIR in input_dir:
                    cmd.append(ATA_IMAGE_DIR)
                cmd.append(new_file)
                cmds_to_run.append(cmd)

        for cmd_to_run in cmds_to_run:
            self.logger.info(f'G: {" ".join(cmd_to_run)}')
            proc = subprocess.run(cmd_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True)
            for line in proc.stdout.split(os.linesep):
                if line != '':
                    self.logger.info(line)

    def prune_date_dirs(self):
        if len(self.date_dirs) > MAX_DIR_COUNT:
            old_dir = self.date_dirs.pop(0)
            self.prune_dir_set(old_dir)

    def prune_dir_set(self, old_date_dir):
        ddirs = [f for f in self.dir_set if old_date_dir in f]
        for ddir in ddirs:
            del self.dir_set[ddir]

    def run(self):
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.check_for_files())
        self.loop.create_task(self.check_for_date_dir())
        self.loop.run_forever()


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

    watcher = Watcher(args.dir, args.test)
    watcher.run()
