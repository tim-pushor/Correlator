import logging
import mako.runtime
from twilio.rest import Client

from Correlator.Event.core import EventListener, Event
from Correlator.config import GlobalConfig, ConfigType

log = logging.getLogger(__name__)

mako.runtime.UNDEFINED = ''

SMSConfig = {

        'twilio.from': {
            'default': '',
            'desc': 'Phone number message will be from',
            'type': ConfigType.STRING
        },

        'twilio.to': {
            'default': '',
            'desc': 'Phone number to deliver the message to',
            'type': ConfigType.STRING
        }
}


class SMS(EventListener):

    GlobalConfig.add(SMSConfig)

    name = 'SMS'

    def __init__(self, account_sid: str, handle_error=True, handle_warning=True,
                 handle_notice=False):

        self.account_sid = account_sid
        self.auth_token = None
        self.Client = None
        self.twilio_from = GlobalConfig.get('twilio.from')
        self.twilio_to = GlobalConfig.get('twilio.to')

        self.handle_warning = handle_warning
        self.handle_notice = handle_notice
        self.handle_error = handle_error

    def credentials_req(self) -> [str]:
        self.auth_token = self.get_creds(self.account_sid)
        if self.auth_token is None:
            return [self.account_sid]

        return []

    def process_event(self, event: Event):

        if event.is_error:
            if not self.handle_error:
                log.debug('Ignoring event type ERROR')
                return
        elif event.is_warning:
            if not self.handle_warning:
                log.debug('Ignoring event type WARNING')
                return
        else:
            if not self.handle_notice:
                log.debug('Ignoring event type NOTICE')
                return

        # Check for errors

        errors = []

        if not self.twilio_to:
            errors.append('The twilio.to parameter must be set')
        if not self.twilio_from:
            errors.append('The twilio.from parameter must be set')

        if errors:
            for error in errors:
                log.error(error)
            return

        if self.Client is None:
            self.Client = Client(self.account_sid, self.auth_token)

        text_detail = event.render_text()

        if text_detail is None:
            text_detail = event.summary

        message = self.Client.messages.create(
            from_=self.twilio_from,
            body=text_detail,
            to=self.twilio_to
        )

        log.info('SMS Sent')