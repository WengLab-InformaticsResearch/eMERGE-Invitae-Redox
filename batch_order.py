import logging
from configparser import ConfigParser
import time
from datetime import date

from errorhandler import ErrorHandler

from redcap_invitae import Redcap
from r4 import R4
from redox import RedoxInvitaeAPI
from emailer import Emailer
from utils import (
    convert_emerge_race_to_redox_race, 
    convert_emerge_race_to_invitae_ancestry, 
    map_redcap_sex_to_redox_sex, 
    get_invitae_primary_indication, 
    describe_patient_history, 
    generate_family_history
    )

if __name__ == "__main__":
    # Setup logging
    error_handler = ErrorHandler(logging.WARNING)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('redox.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
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
    # R4
    r4_api_endpoint = parser.get('R4', 'R4_URL')
    r4_api_token = parser.get('R4', 'R4_API_KEY')    
    # Redox
    redox_api_base_url = parser.get('REDOX', 'BASE_URL')
    redox_api_key =  parser.get('REDOX', 'REDOX_API_KEY')
    redox_api_secret = parser.get('REDOX', 'REDOX_API_SECRET')
    query_wait_sec = parser.getint('REDOX', 'WAIT_BEFORE_ORDER_QUERY_SECONDS', fallback=0)
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

    # R4 configuration
    r4 = R4(r4_api_endpoint, r4_api_token)

    # While we're developing the script, force double check of which projects we're working on
    CHECK_BEFORE_RUNNING = development
    redcap_project_title = redcap.project.export_project_info()['project_title']
    r4_project_title = r4.export_project_info()['project_title']
    if CHECK_BEFORE_RUNNING:
        msg = f'Working on\nRedcap project: {redcap_project_title}\nR4 project: {r4_project_title}.\nEnter the "YeS" to continue:\n'
        if input(msg) != "YeS":
            print('Exiting')
            exit()    

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
        logger.debug('; '.join(f"{p[Redcap.FIELD_RECORD_ID]}: {p[Redcap.FIELD_NAME_FIRST]} {p[Redcap.FIELD_NAME_LAST]}" for p in participant_info))
        if CHECK_BEFORE_RUNNING and (input('Enter "yes" to continue: ') != 'yes'):
            logger.debug('Exiting script prior to sending Redox orders.')
            exit()

        for p in participant_info:
            order_id = redcap.get_new_order_id()
            local_id = p[Redcap.FIELD_RECORD_ID]
            r4_record_id = p[Redcap.FIELD_R4_RECORD_ID]
            logger.debug(f'Processing participant CUIMC {local_id}, R4 {r4_record_id}')
            
            order_log = p[Redcap.FIELD_ORDER_LOG]
            if order_log:
                # Add a visual separator
                order_log += '==========================\n'
            
            # Map sex, race, and ancestry data from eMERGE to Redox / Invitae values
            sex = map_redcap_sex_to_redox_sex(p[Redcap.FIELD_SEX])
            redox_race = convert_emerge_race_to_redox_race(p)
            invitae_ancestry = convert_emerge_race_to_invitae_ancestry(p)

            # Invitae AOE questions get primary indication and description of health history from baseline survey data
            primary_indication = get_invitae_primary_indication(p)
            patient_history = describe_patient_history(p)
            # Mark patient as affected / symptomatic when patient history is not empty
            affected_symptomatic = 'Yes' if patient_history else 'No'

            # Get family health history from MeTree
            # Get MeTree JSON from R4
            metree = r4.get_metree_json(r4_record_id)
            if metree:
                family_history, family_count = generate_family_history(metree)
                has_family_history = 'Yes' if family_count > 0 else 'No'
            else:
                has_family_history = 'No'
                family_history = ''

            success, msg = redox.put_new_order(patient_id=p[Redcap.FIELD_LAB_ID],
                                        patient_name_first=p[Redcap.FIELD_NAME_FIRST],
                                        patient_name_last=p[Redcap.FIELD_NAME_LAST],
                                        patient_dob=p[Redcap.FIELD_DOB],
                                        patient_sex=sex,
                                        patient_redox_race=redox_race,
                                        patient_invitae_ancestry=invitae_ancestry,
                                        order_id=order_id,
                                        prim_ind=primary_indication, 
                                        is_ind_aff=affected_symptomatic, 
                                        pat_hist=patient_history,
                                        has_fam_hist=has_family_history, 
                                        fam_hist=family_history,
                                        test=development)
            
            # Record status
            datestr = date.today().isoformat()
            if success:
                order_log += f'Order ID {order_id} successfully submitted on {datestr}:\n{msg}\n'
                redcap.update_order_status(record_id=local_id,
                                        order_new=Redcap.YesNo.NO,
                                        order_status=Redcap.OrderStatus.SUBMITTED,
                                        order_date=datestr,
                                        order_id=order_id,
                                        order_log=order_log,
                                        form_complete=Redcap.FormComplete.UNVERIFIED)
            else:
                order_log += f'Order ID {order_id} attempt failed on {datestr}.\n'
                redcap.update_order_status(record_id=local_id,
                                        order_new=Redcap.YesNo.NO,
                                        order_status=Redcap.OrderStatus.FAILED,
                                        order_date=datestr,
                                        order_id=order_id,
                                        order_log=order_log,
                                        form_complete=Redcap.FormComplete.INCOMPLETE)

    ##################################################################################
    # Invitae currently does not support order status checks. Code below commented out
    ################################################################################## 

    # # Give Invitae a little time before querying for order status
    # if query_wait_sec > 0:
    #     time.sleep(query_wait_sec)

    # # Check the status of pending orders
    # participant_info = redcap.pull_info_for_query_order()
    # if not participant_info:
    #     logger.info('No order statuses need to be checked')
    # else:
    #     # Currently in development. Show what information has been collecetd and verify before continuing to send data out
    #     logger.debug('The following participant data have been collected for checking order status:')
    #     logger.debug(participant_info)
    #     if input('Enter "yes" to continue: ') != 'yes':
    #         logger.debug('Exiting script prior to checking Redox order statuses.')
    #         exit()

    #     for p in participant_info:
    #         response = redox.query_order(patient_id=p[Redcap.FIELD_LAB_ID])
    #         if not response:
    #             next

    #         current_status = p[Redcap.FIELD_ORDER_STATUS]

    #         # Fake status update for testing
    #         if current_status == '2':
    #             new_status = Redcap.OrderStatus.RECEIVED
    #         elif current_status == '3':
    #             new_status =Redcap.OrderStatus.COMPLETED
    #         redcap.update_order_status(record_id=p[Redcap.FIELD_RECORD_ID],
    #                                 order_status=new_status)

    if error_handler.fired:
        emailer.sendmail('Invitae Redox API issue', 'An issue occurred in the Invitae Redox script. Please check the logs.')
