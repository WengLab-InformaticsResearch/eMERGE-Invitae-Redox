### Send out email via Redcap

- By default, only MX record but not SMTP server setup. Potential error is the email can not be sent to external domains.
- To setup SMTP server, you need to config `sendmail` program, which is used by RedCap
  - Check [here](./https://www.snel.com/support/smtp-relay-with-sendmail/) for details
  - The most important part is edit `/etc/mail/sendmail.mc` and change the following line
  ```sh
  define(`SMART_HOST', `you.smtp.server.domain')dnl
  define(`RELAY_MAILER',`esmtp')dnl
  define(`RELAY_MAILER_ARGS', `TCP $h 587')dnl
  ```
- Check log `sudo tail /var/log/mail.log` for sending details
- For CUIMC only
  - you need to send a tick to CUIMC IT to request to use CUIMC email secure SMTP server. (secure nova?). For the general one, you will get a SPF warning.
