import logging
from configparser import ConfigParser
import time
from datetime import date

from errorhandler import ErrorHandler

from redcap_invitae import Redcap
from redox import RedoxInvitaeAPI
from emailer import Emailer
from utils import convert_emerge_race_to_redox_race

if __name__ == "__main__":
    # Setup logging
    error_handler = ErrorHandler(logging.WARNING)
    logger = logging.getLogger('redox_application')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('redox.log')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info('Begin Invitae Redox batch script')

    # Read config file
    parser = ConfigParser(inline_comment_prefixes=['#'])
    parser.read('./redox-api.config')
    # Development environment configuraiton
    development = parser.getboolean('GENERAL', 'DEVELOPMENT')
    # REDCap
    redcap_api_endpoint = parser.get('REDCAP', 'LOCAL_REDCAP_URL')
    redcap_api_token = parser.get('REDCAP', 'LOCAL_REDCAP_API_KEY')
    # Redox
    redox_api_base_url = parser.get('REDOX', 'BASE_URL')
    redox_api_key =  parser.get('REDOX', 'REDOX_API_KEY')
    redox_api_secret = parser.get('REDOX', 'REDOX_API_SECRET')
    query_wait_sec = parser.getint('REDOX', 'WAIT_BEFORE_ORDER_QUERY_SECONDS', fallback=0)
    # Order
    facility_code = parser.get('ORDER', 'FACILITY_CODE')
    provider_npi = parser.get('ORDER', 'PROVIDER_NPI')
    provider_name_first = parser.get('ORDER', 'PROVIDER_NAME_FIRST')
    provider_name_last = parser.get('ORDER', 'PROVIDER_NAME_LAST')
    # Email
    email_host = parser.get('EMAIL', 'SMTP_HOST')
    email_port = parser.get('EMAIL', 'SMTP_PORT')
    email_from = parser.get('EMAIL', 'FROM_ADDR')
    email_to = parser.get('EMAIL', 'TO_ADDRS')
    email_to = [e.strip() for e in email_to.split(';') if e.strip()]  # split emails by ; and get rid of empty

    # Emailer to notify dev of failures
    emailer = Emailer(email_host, email_port, email_from, email_to)

    # Redcap configuration
    redcap = Redcap(redcap_api_endpoint, redcap_api_token)

    # Redox configuration and authentication
    redox = RedoxInvitaeAPI(redox_api_base_url, redox_api_key, redox_api_secret)
    if not redox.authenticate():
        msg = 'Unable to authenticate with Redox. Exiting without processing any orders.'
        logger.error(msg)
        emailer.sendmail('Invitae Redox API issue', msg)
        exit()

    # Place new orders with Invitae
    participant_info = redcap.pull_info_for_new_order()
    if not participant_info:
        logger.info('No new orders are needed')
    else:
        # Currently in development. Show what information has been collecetd and verify before continuing to send data out
        logger.debug('The following participant data have been collected for placing new orders:')
        logger.debug(participant_info)
        if input('Enter "yes" to continue: ') != 'yes':
            logger.debug('Exiting script prior to sending Redox orders.')
            exit()

        for p in participant_info:
            order_id = redcap.get_new_order_id()
            
            redox_race = convert_emerge_race_to_redox_race(participant_info)

            success = redox.put_new_order(facility_code=facility_code,
                                        patient_id=p[Redcap.FIELD_LAB_ID],
                                        patient_name_first=p[Redcap.FIELD_NAME_FIRST],
                                        patient_name_last=p[Redcap.FIELD_NAME_LAST],
                                        patient_dob=p[Redcap.FIELD_DOB],
                                        patient_sex=p[Redcap.FIELD_SEX],
                                        patient_race=redox_race,
                                        provider_npi=provider_npi,
                                        provider_name_first=provider_name_first,
                                        provider_name_last=provider_name_last,
                                        order_id=order_id,
                                        test=development)
            if success:
                redcap.update_order_status(record_id=p[Redcap.FIELD_RECORD_ID],
                                        order_new=Redcap.YesNo.NO,
                                        order_status=Redcap.OrderStatus.SUBMITTED,
                                        order_date=date.today().isoformat(),
                                        order_id=order_id)

    # Give Invitae a little time before querying for order status
    if query_wait_sec > 0:
        time.sleep(query_wait_sec)

    # Check the status of pending orders
    participant_info = redcap.pull_info_for_query_order()
    if not participant_info:
        logger.info('No order statuses need to be checked')
    else:
        # Currently in development. Show what information has been collecetd and verify before continuing to send data out
        logger.debug('The following participant data have been collected for checking order status:')
        logger.debug(participant_info)
        if input('Enter "yes" to continue: ') != 'yes':
            logger.debug('Exiting script prior to checking Redox order statuses.')
            exit()

        for p in participant_info:
            response = redox.query_order(patient_id=p[Redcap.FIELD_LAB_ID])
            if not response:
                next

            current_status = p[Redcap.FIELD_ORDER_STATUS]

            # Fake status update for testing
            if current_status == '2':
                new_status = Redcap.OrderStatus.RECEIVED
            elif current_status == '3':
                new_status =Redcap.OrderStatus.COMPLETED
            redcap.update_order_status(record_id=p[Redcap.FIELD_RECORD_ID],
                                    order_status=new_status)

    if error_handler.fired:
        emailer.sendmail('Invitae Redox API issue', 'An issue occurred in the Invitae Redox script. Please check the logs.')
