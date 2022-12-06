#!python3


import argparse
import logging
from py.log import LogHelper, LogfileProcessor
from py.notify import Notifiers, ConsoleNotify, CSVNotify
from py.ucpath_queue import I280Queue

log = logging.getLogger('logger')

parser = argparse.ArgumentParser('Log Analyzer')
parser.add_argument(
    '--d', action='store_true', help='Debug mode')
parser.add_argument(
    '--csv', action='store_true',
    help='Write audit data for each module to csv files')
parser.add_argument('logfile', help='Log file to parse')
args = parser.parse_args()

# Set up the notifier chain

notifiers = Notifiers()
# Add the basic console notifier
notifiers.add_notifier(ConsoleNotify())
if args.csv:
    # add the CSV notifier if requested.
    notifiers.add_notifier(CSVNotify())

# List of modules

modules = [
    I280Queue
]

# Debugging

debug_level = logging.DEBUG if args.d else logging.INFO

LogHelper.initialize_console_logging(log, debug_level)

log.info('Starting')
app = LogfileProcessor(notifiers, modules, log)
app.from_file(args.logfile)
app.log_stats()





