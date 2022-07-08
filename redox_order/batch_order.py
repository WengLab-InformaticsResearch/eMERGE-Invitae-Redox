import logging
from configparser import ConfigParser
import time
from datetime import date

from redcap import Redcap
from redox import RedoxInvitaeAPI

if __name__ == "__main__":
    # Setup logging
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

    # Read config file
    parser = ConfigParser()
    parser.read('./redox-api.config')
    redcap_api_endpoint = parser.get('REDCAP', 'LOCAL_REDCAP_URL')
    redcap_api_token = parser.get('REDCAP', 'LOCAL_REDCAP_API_KEY')
    redox_api_key =  parser.get('REDOX', 'REDOX_API_KEY')
    redox_api_secret = parser.get('REDOX', 'REDOX_API_SECRET')
    query_wait_sec = parser.getint('REDOX', 'WAIT_BEFORE_ORDER_QUERY_SECONDS', 0)

    # Redcap configuration
    redcap = Redcap(redcap_api_endpoint, redcap_api_token)

    # Redox configuration and authentication
    redox = RedoxInvitaeAPI(redox_api_key, redox_api_secret)
    if not redox.authenticate():
        logger.error('Unable to authenticate with Redox. Exiting without processing any orders.')

        # TODO: Notify developers of issue

        exit()

    # Place new orders with Invitae
    participant_info = redcap.pull_info_for_new_order()
    if not participant_info:
        logger.info('No new orders are needed')

    for p in participant_info:
        success = redox.put_new_order(patient_id=p[Redcap.FIELD_LAB_ID])
        if success:
            redcap.update_order_status(record_id=p[Redcap.FIELD_RECORD_ID],
                                       order_status=Redcap.OrderStatus.SUBMITTED,
                                       order_date=date.today().isoformat(),
                                       order_id='COLUMBIA_ORDER_314159')
        else:
            # TODO: notify someone of order error
            pass

    # Give Invitae a little time before querying for order status
    if query_wait_sec > 0:
        time.sleep(query_wait_sec)

    # Check the status of pending orders
    participant_info = redcap.pull_info_for_query_order()
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
