import argparse
import logging
import os
import sys
import re
from datetime import datetime
from typing import List

from Correlator.config import GlobalConfig
from Correlator.Event.core import EventProcessor
from Correlator.Module.report import Report
from Correlator.syslog import (SyslogServer, SyslogStatsEvent, SyslogRecord,
                               RawSyslogRecord)
from Correlator.util import (setup_root_logger, capture_filename,
                             format_timestamp, Module)


class BaseCLI:

    cli_title: str = 'Correlator Syslog CLI utility'

    def add_arguments(self, parser: argparse.ArgumentParser):
        raise NotImplementedError

    def modify_stack(self, cmd_args: argparse.Namespace,
                     modules: List[Module], processor: EventProcessor):
        raise NotImplementedError

    @staticmethod
    def syslog_record_model():
        return SyslogRecord

    @staticmethod
    def trailer_discovery_method(
            raw_record: RawSyslogRecord) -> bytes | None:
        return None

    # todo Customize epilog

    def __init__(self):

        parser = argparse.ArgumentParser(
            self.cli_title,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__doc__)

        parser.add_argument(
            '--d',
            help='Debug level', action='store_true'
        )
        parser.add_argument(
            '--port',
            help='TCP port to listen on', type=str)

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
            metavar='filename',
            help='raw syslog capture file to read and process')

        parser.add_argument(
            '--store-file',
            metavar='filename',
            help='File to save and load the persistence store '
                 'from')

        parser.add_argument(
            '--o',
            action='append',
            metavar='option.name=value',
            help='Set Correlator option.name to value'
        )

        parser.add_argument(
            '--config',
            action='store_true',
            help='*ONLY* show the valid configuration options and their values '
                 'then exit'
        )

        parser.add_argument(
            '--email',
            metavar='address',
            help='Enable email handler and send emails to this '
                 'address')

        parser.add_argument(
            '--sms',
            metavar='Twilio Account SID',
            help='Enable SMS handler and use this SID for twilio')

        parser.add_argument(
            '--sms-to',
            metavar='Phone Number',
            help='Value to populate twilio SMS \'To\' field',
        )

        parser.add_argument(
            '--sms-from',
            metavar='Phone Number',
            help='Value to populate twilio SMS \'From\' field',
        )

        parser.add_argument(
            '--csv',
            metavar='filename', nargs='?', default='.',
            help='Write audit records as rows in CSV files'
        )

        self.add_arguments(parser)

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

        # SMS

        if cmd_args.sms:
            if not cmd_args.sms_to:
                parser.error('--sms-to is required when using --sms')
            if not cmd_args.sms_from:
                parser.error('--sms-from is required when using --sms')

        csv_module = None

        if cmd_args.csv != '.':  # . = not on command line
            from Correlator.Event.csv_writer import CSVListener
            if cmd_args.csv is not None:
                log.info(f'Writing CSV files: {cmd_args.csv}')
                csv_module = CSVListener(
                    [x.strip() for x in cmd_args.csv.split()])
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

        if cmd_args.sms:
            from Correlator.Event.sms_sender import SMS
            GlobalConfig.set('twilio.to', cmd_args.sms_to)
            GlobalConfig.set('twilio.from', cmd_args.sms_from)
            processor.register_listener(SMS(cmd_args.sms))

        # Setup list of logic modules

        modules = []

        # Allow subclass to modify the stack

        self.modify_stack(cmd_args, modules, processor)

        # If any weren't added, add the Report module

        if not modules:
            log.debug('No configured modules. Enabling Report module')
            modules.append(Report())

        # Check if creds required for any event handlers

        ids = processor.check_creds()

        if ids:
            for userid in ids:
                log.error(f'A password for id {userid} was not found in the credential store')
            log.info('Shutting down due to missing passwords')
            sys.exit(0)

        if cmd_args.port:
            GlobalConfig.set('syslog_server.listen_port', cmd_args.port)
        if cmd_args.host:
            GlobalConfig.set('syslog_server.listen_address', cmd_args.host)

        # Process Correlator configuration entry overrides

        if cmd_args.o:
            for entry in cmd_args.o:
                m = re.match(r'(.+)=(.+)', entry)
                if m:
                    (key, value) = (m.group(1), m.group(2))
                    GlobalConfig.set(key, value)
                    log.debug(f'Option {key} overridden to {value}')

        if cmd_args.config:
            GlobalConfig.dump_to_log(debug=False)
            log.info('Shutting down after configuration query')
            sys.exit(0)
        else:
            GlobalConfig.dump_to_log()

        server = SyslogServer(modules,
                              processor,
                              record=self.syslog_record_model(),
                              store_file=cmd_args.store_file,
                              discovery_method=self.trailer_discovery_method)

        start = datetime.now()

        if cmd_args.read_file:
            # Replay from capture file
            log.info(f'Reading from capture file {cmd_args.read_file}')
            server.from_file(open(cmd_args.read_file, 'rb'))

        else:
            server.listen_single(output_file=output_file)

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