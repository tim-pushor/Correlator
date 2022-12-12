import logging
import sys


class ParserError(Exception):
    pass


class LogHelper:

    @staticmethod
    def initialize_console_logging(log, log_level):
        ch = logging.StreamHandler(sys.stdout)

        ch.setLevel(log_level)
        log.setLevel(log_level)

        formatter = logging.Formatter(
            '%(asctime)s: %(levelname)s: %(message)s',
            '%Y-%m-%d %H:%M:%S')

        ch.setFormatter(formatter)
        log.addHandler(ch)


def build_modules(modules, notifiers, log):
    moduledict = {}
    for module in modules:
        obj = module(notifiers, log)
        moduledict[obj.identifier] = obj
    return moduledict