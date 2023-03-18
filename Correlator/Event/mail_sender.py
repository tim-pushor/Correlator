import logging
import smtplib
import os

from mako.template import Template
from email import message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Correlator.Event.core import EventListener, Event
from Correlator.config import GlobalConfig
from Correlator.util import template_dir, Instance

log = logging.getLogger(__name__)

EmailConfig = {
        'email.smtp_server': {
            'default': 'giganode1',
            'desc': 'SMTP Server'
        },
        'email.from': {
            'default': 'admin@nowhere.com',
            'desc': 'Value of the Email From: Field'
        },
        'email.to': {
            'default': 'nobody',
            'desc': 'Value of the Email To: Field'
        },
}


class Email(EventListener):

    GlobalConfig.add(EmailConfig)

    def __init__(self, handle_error=True, handle_warning=True,
                 handle_notice=True):

        self.template_dir = template_dir()
        self.html_email = True

        self.smtp_server = GlobalConfig.get(
            'email.smtp_server')

        self.email_from = GlobalConfig.get(
            'email.from')

        self.email_to = GlobalConfig.get(
            'email.to')

        self.handle_warning = handle_warning
        self.handle_notice = handle_notice
        self.handle_error = handle_error

    def process_event(self, event: Event):

        if event.is_error:
            if not self.handle_error:
                log.debug('Ignoring event type ERROR')
                return
            template_name = 'email-error.mako'
        elif event.is_warning:
            if not self.handle_warning:
                log.debug('Ignoring event type WARNING')
                return
            template_name = 'email-warming.mako'
        else:
            if not self.handle_notice:
                log.debug('Ignoring event type NOTICE')
                return
            template_name = 'email-notice.mako'

        html_detail = event.render_html()
        text_detail = event.render_text()

        if text_detail is None:
            text_detail = event.summary

        html_content = None
        if event.audit_desc is not None:
            summary = event.audit_desc
        else:
            summary = event.summary

        # Render text message body

        template_path = os.path.join(self.template_dir, template_name)

        if not os.path.isfile(template_path):
            raise ValueError(f'Required template {template_path} missing')

        data = {
            'version': Instance.Version,
            'text_detail': text_detail,
            'html_detail': html_detail,
            'summary': summary
            }

        if html_detail and self.html_email:
            # Render HTML message body
            html_content = Template(
                filename=template_path).get_def('body_html').render(**data)

        email_template = Template(filename=template_path)
        text_content = email_template.get_def('body_text').render(**data)
        subject = email_template.get_def('subject').render(**data)

        if html_content:
            msg = MIMEMultipart('alternative')
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
        else:
            msg = message.Message()
            msg.add_header('Content-Type', 'text')
            msg.set_payload(text_content)

        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Subject'] = subject

        log.info(f'Sending email to {self.email_to}')

        smtp = smtplib.SMTP(self.smtp_server)
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())



