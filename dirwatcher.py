#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""


import sys
import argparse
import logging
import signal
import os
import time
import datetime

__author__ = """
stephguirand
Help from demo, lessons and activities, youtube videos in canvas and
own search on youtube,
stack overflow, Tutors, Facilitators and talking about assignment
in study group.
"""

files_found = []
magic_string_position = {}
exit_flag = False
banner_text = '\n' + '-' * 60 + '\n'


logger = logging.getLogger(__name__)


def set_logger():
    """set up logger to print """


log_format = ('%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s'
              '[%(threadName)-12s] %(message)s')
logging.basicConfig(level=logging.INFO, format=log_format,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout
                    )

logger.setLevel(logging.DEBUG)


"""
break up your code into small functions such as `scan_single_file()`,
`detect_added_files()`, `detect_removed_files()`, and `watch_directory()`
-Events to log are startup banner, shutdown banner, exceptions, magic text
found events, files added or removed from watched dir, and OS signal events.
"""


def set_banner(run_shut_text, start_uptime_text, app_time):
    """Setup Startup/Shutdown Banner"""
    logger.info(
        f'{banner_text}' + '{0} {2}\n  {1} {3}\n'.format(
            run_shut_text,
            start_uptime_text,
            __name__,
            app_time) + f'{banner_text}'
    )


def detect_added_files(extension, path):
    """ search for magic word"""
    global files_found
    global magic_string_position
    for s_file in files_found:
        if s_file.endswith(extension) and s_file not in magic_string_position:
            magic_string_position[s_file] = 0
            logger.info(f'New file: {s_file} found in {path}')


def detect_removed_files(path):
    """ Track files"""
    global files_found
    global magic_string_position
    files_to_remove = []
    for s_file in magic_string_position.keys():
        if s_file not in files_found:
            files_to_remove.append(s_file)
    for file in files_to_remove:
        del magic_string_position[file]
        logger.info(f'File: {file} is removed, Removed from: {path}')


def search_for_magic(filename, path, magic_string):
    """Search for the magic word in the filename line by line and
    keep track of the last line searched"""
    global files_found
    global magic_string_position
    file_path = os.path.join(path, filename)
    try:
        with open(file_path, 'r') as f:
            for i, line in enumerate(f.readlines(), 1):
                if i > magic_string_position[filename]:
                    magic_string_position[filename] += i
                    if magic_string in line:
                        logger.info(f'Magic string: {magic_string} found on\
                            line: {i} in file: {filename}')
    except OSError:
        logger.info(f'{filename} not found')


def watch_directory(path, magic_string, extension):
    """ Watches a given directory for instances of a magic search"""
    global magic_string_position
    global files_found

    try:
        files_found = [f for f in os.listdir(
            path) if os.path.isfile(os.path.join(path, f))]
    except OSError:
        logger.info(f'{path} does not exist')
    else:
        # Check for new files
        detect_added_files(extension, path)

        # Stop watching deleted files
        detect_removed_files(path)

        # Scan watched files
        for s_file in files_found:
            search_for_magic(s_file, path, magic_string)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Watches a directory for files containing magic text')
    parser.add_argument(
        '-i', '--interval', type=float, default=1.0, help='Polling interval for\
            program',)
    parser.add_argument(
        '-e', '--extension', type=str, default=".txt", help='Extension of file\
            to search for',)
    parser.add_argument('path', help='Directory to be searched')
    parser.add_argument('magic_string', help='Magic string to watch for')
    return parser


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here
    as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if
    the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """

    global exit_flag
    exit_flag = True
    logger.warning('Received ' + signal.Signals(sig_num).name)
    return


def main(args):
    """ parses command line and launches forever while loop"""
    global magic_string_position

    # Hook these two signals from the OS ..
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = create_parser()
    p_args = parser.parse_args(args)

    if not p_args:
        parser.print_usage(args)
        sys.exit(1)

    # Call set_logger for set up logger
    set_logger()
    path = p_args.path
    magic_string = p_args.magic_string
    interval = p_args.interval
    extension = p_args.extension

    # Set start time for running app
    start_time = datetime.datetime.now()

    # Setup Startup Banner
    set_banner('Running', 'Started on', start_time.isoformat())

    # log with directory name, file extension and magic text which we find
    logger.info(
        f'Watching directory: {path} for files ending\
            with: {extension} containing magic\
                text: {magic_string} every {interval} seconds')

    # Watching directory until exit_flag set true
    while not exit_flag:
        try:
            # call directory watching function
            watch_directory(path, magic_string,
                            extension)
            # Log an ERROR level message here
        except Exception as e:
            # This is an UNHANDLED exception
            logger.exception(f'UNHANDLED exception: {e}')
            # logger.info("Program uptime: {} seconds".format(
        finally:

            # put a sleep inside my while loop so I don't peg the cpu usage at
            # 100%
            time.sleep(interval)

    # Setup Shutdown Banner
    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start
    uptime = datetime.datetime.now() - start_time
    set_banner('Shutting down', 'Uptime was', (uptime))


if __name__ == '__main__':
    main(sys.argv[1:])
