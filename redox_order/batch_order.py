import logging
from configparser import ConfigParser
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

    # Redcap configuration
    redcap = Redcap(redcap_api_endpoint, redcap_api_token)

    # Redox configuration and authentication
    redox = RedoxInvitaeAPI(redox_api_key, redox_api_secret)
    if not redox.authenticate():
        logger.error('Unable to authenticate with Redox. Exiting without processing any orders.')

        # TODO: Notify developers of issue

        exit()

    # Place new orders with Invitae
    id_for_ordering = redcap.pull_batch_ids()
    if id_for_ordering is None:
        logger.info('No new orders are needed')
        exit()
    for participant_id in id_for_ordering:
        success = redox.put_new_order(patient_id=participant_id)
        if not success:
            next
        success = redox.query_order(patient_id=participant_id)
        if not success:
            next
        redcap.update_order_status(participant_id=participant_id)


