""" Reference syslog server included with the Correlator library

- Reads from the network or capture file, optionally writing records received
  over the network to a capture file.
- Use or test modules included with this library.


"""

import argparse
import logging
import os
import sys
from datetime import datetime

from Correlator.config import GlobalConfig
from Correlator.Event.core import EventProcessor
from Correlator.Module.report import Report
from Correlator.syslog import SyslogServer, SyslogStatsEvent
from Correlator.util import (
    setup_root_logger, capture_filename, format_timestamp)


def cli():

    parser = argparse.ArgumentParser(
        'Correlator Syslog CLI utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)

    parser.add_argument(
        '--d',
        help='Debug level', action='store_true'
    )
    parser.add_argument(
        '--port',
        help='TCP port to listen on', type=int)

    parser.add_argument(
        '--host',
        help='Address to listen on', type=str)

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '--write-file',
        metavar='filename', nargs='?', default='.',
        help='File to capture records and save to raw syslog capture file')

    group.add_argument(
        '--read-file',
        metavar='filename', help='raw syslog capture file to read and process')

    parser.add_argument(
        '--sshd',
        action='store_true', help='Activate ssh login module')

    parser.add_argument(
        '--store-file',
        metavar='filename', help='File to save and load the persistence store '
                                 'from')

    parser.add_argument(
        '--email',
        metavar='address', help='Enable email handler and send emails to this '
                                'address')
    parser.add_argument(
        '--csv',
        metavar='filename', nargs='?', default='.',
        help='Write audit records as rows in CSV files'
    )

    cmd_args = parser.parse_args()

    # Setup logging

    debug_level = logging.DEBUG if cmd_args.d else logging.INFO
    setup_root_logger(debug_level)
    log = logging.getLogger(__name__)

    # Give a default value to write_file if not provided

    d = vars(cmd_args)

    if cmd_args.write_file is None:
        d['write_file'] = capture_filename()
    elif cmd_args.write_file == '.':
        d['write_file'] = None

    csv_module = None

    if cmd_args.csv != '.':     # . = not on command line
        from Correlator.Event.csv_writer import CSVListener
        if cmd_args.csv is not None:
            log.info(f'Writing CSV files: {cmd_args.csv}')
            csv_module = CSVListener([x.strip() for x in cmd_args.csv.split()])
        else:
            log.info('Writing CSV files: All')
            csv_module = CSVListener()

    output_file = None

    if cmd_args.write_file:
        if os.path.exists(cmd_args.write_file):
            print(f'{cmd_args.write_file} exists. Delete it first')
            sys.exit(0)
        else:
            log.info(f'Writing received syslog data to capture file '
                     f'{cmd_args.write_file}')
            output_file = open(cmd_args.write_file, 'wb')

    # Initialize event processor, and add event listeners

    processor = EventProcessor()
    from Correlator.Event.log import LogbackListener
    processor.register_listener(LogbackListener())

    if csv_module is not None:
        processor.register_listener(csv_module)
    if cmd_args.email:
        from Correlator.Event.mail_sender import Email
        GlobalConfig.set('email.to', cmd_args.email)
        processor.register_listener(Email())

    # Setup list of logic modules

    modules = []

    # Add all modules specified on the command line

    if cmd_args.sshd:
        from Correlator.Module.sshd import SSHD
        modules.append(SSHD())

    # If any weren't added,add the Report module

    if not modules:
        modules.append(Report())

    if cmd_args.port:
        GlobalConfig.set('syslog_server.listen_port', int(cmd_args.port))
    if cmd_args.host:
        GlobalConfig.set('syslog_server.listen_address', cmd_args.host)

    server = SyslogServer(modules, processor, store_file=cmd_args.store_file)

    start = datetime.now()

    if cmd_args.read_file:
        # Replay from capture file
        log.info(f'Reading from capture file {cmd_args.read_file}')
        server.from_file(open(cmd_args.read_file, 'rb'))

    else:
        stop = False
        while not stop:
            try:
                server.listen_single(output_file=output_file)
            except KeyboardInterrupt:
                log.info('Shutting down')
                server.save_store()
                stop = True

    end = datetime.now()

    for module in modules:
        module.statistics()

    e = SyslogStatsEvent(
        {
            'start': format_timestamp(start),
            'end': format_timestamp(end),
            'duration': str(end - start)
        })
    e.system = 'syslog-server'
    processor.dispatch_event(e)


if __name__ == '__main__':
    cli()
