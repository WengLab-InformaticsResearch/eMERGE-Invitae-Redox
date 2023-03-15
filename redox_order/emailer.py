import logging
import smtplib
import sys

_MESSAGE_FORMAT = """Subject: {subject}

{body}
"""

logger = logging.getLogger(__name__)

class Emailer():
    def __init__(self, host='localhost', port=25, from_addr=None, to_addrs=None):
        self._host = host
        self._port = port
        # Default from and to email addresses
        self._from_addr = from_addr
        self._to_addrs = to_addrs

    def sendmail(self, subject, body, from_addr=None, to_addrs=None):
        if not from_addr:
            from_addr = self._from_addr
        if not to_addrs:
            to_addrs = self._to_addrs

        if not from_addr or not to_addrs or not self._host or not self._port:
            logging.error('Incorrect email configuration')
            return

        with smtplib.SMTP(self._host, self._port) as smtp_obj:
            try:
                message = _MESSAGE_FORMAT.format(subject=subject, body=body)
                smtp_obj.sendmail(from_addr, to_addrs, message)
            except smtplib.SMTPException:
                logging.error(f'Error sending email: {sys.exc_info()[0]}')
