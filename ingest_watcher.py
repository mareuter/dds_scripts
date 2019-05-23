import argparse
import logging
import logging.handlers
import os
import subprocess
import time

LOG_NAME = "ingest_watcher"
LOG_FILE_SIZE = 1000000  # 1 MB
LOG_FILES_TO_KEEP = 10

OUTPUT_FILE_EXT = ".fits"


class Watcher:

    logger = logging.getLogger(LOG_NAME)

    def __init__(self, input_dir=None, test_mode=False):
        self.test_mode = test_mode
        if input_dir is None:
            pass
        else:
            self.dirs = [input_dir]

        self.dir_set = {}
        for idir in self.dirs:
            self.dir_set[idir] = None

    def process(self, input_dir, new_files):
        cmds_to_run = []
        if self.test_mode:
            for new_file in new_files:
                cmds_to_run.append(['python', 'process_file.py', os.path.join(input_dir, new_file)])

        for cmd_to_run in cmds_to_run:
            self.logger.info(f'G: {" ".join(cmd_to_run)}')
            proc = subprocess.run(cmd_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True)
            for line in proc.stdout.split(os.linesep):
                if line != '':
                    self.logger.info(line)

    def run(self):
        for ldir in self.dirs:
            cfiles = set([f for f in os.listdir(ldir)
                          if os.path.isfile(os.path.join(ldir, f)) and f.endswith(OUTPUT_FILE_EXT)])

            ofiles = self.dir_set[ldir]
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
    while True:
        watcher.run()
        time.sleep(10)
