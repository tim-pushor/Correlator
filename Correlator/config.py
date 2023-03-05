import logging
from copy import deepcopy

log = logging.getLogger(__name__)


ConfigConfig = {

    'syslog_server.accept_heartbeat_interval': {
        'default': 5,
        'desc': 'approximate time in seconds between heartbeats while waiting'
                ' for a connection'
    },
    'syslog_server.recv_heartbeat_interval': {
        'default': 5,
        'desc': 'approximate time in seconds between heartbeats while waiting'
                ' for syslog data'
    },
    'syslog_server.save_state_interval': {
        'default': 5,
        'desc': 'approximate time in seconds between state saves'
    },
    'syslog_server.default_buffer_size': {
        'default': 4096,
        'desc': 'Read buffer size. This must be large enough so that an '
                'entire header and structured data can fit.'
    },
    'syslog_server.default_trailer': {
        'default': '\n',
        'desc': 'The default syslog trailer.'
    },

}


class ConfigStore:
    def __init__(self):
        self.store = deepcopy(ConfigConfig)
        pass

    def add(self, item):

        if isinstance(item, list):
            items = item
        else:
            items = [item]

        for item in items:
            self.store.update(item)

    def _assert_parameter(self, parameter):
        if parameter not in self.store:
            raise ValueError(f'Unknown configuration parameter: {parameter}')

    def set(self, parameter, value):
        self._assert_parameter(parameter)
        self.store[parameter]['value'] = value

    def get(self, parameter):
        self._assert_parameter(parameter)
        return self.store[parameter].get(
            'value', self.store[parameter].get('default'))

    def list(self):
        """Returns list of list all configuration parameters

        Plus the description, the current value, and the default value

        [
            [parameter, description, default value, current value]
        ]

        """

        return [
            [x,
             self.store[x].get('desc'),
             self.store[x].get('default'),
             self.store[x].get('value', self.store[x].get('default'))
             ] for x in self.store
        ]

    @staticmethod
    def debug(description=True):

        log.debug(f'{"Parameter":<45} {"Value":<10} {"Default":<10} '
                  f'{"Description":<14}')
        log.debug(f'{"---------":<45} {"------":<10} {"-------":<10} '
                  f'{"-----------------------":<14}')

        for (parameter, description, default, current) in GlobalConfig.list():
            log.debug(f'{parameter or "":<45} {repr(current or ""):<10} '
                      f'{repr(default or ""):<10} {description or "":<14}')


GlobalConfig = ConfigStore()
