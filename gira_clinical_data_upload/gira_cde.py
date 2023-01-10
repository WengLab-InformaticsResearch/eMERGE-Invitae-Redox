import logging
from configparser import ConfigParser
from datetime import date, datetime
from pprint import pprint

import redcap_enums as renums
from redcap_cde import RedcapCDE
from r4_gira_clin_var import R4GiraClinVar
import omop_cde
from emailer import Emailer
from errorhandler import ErrorHandler

if __name__ == "__main__":
    try:
        # Setup logging
        error_handler = ErrorHandler(logging.WARNING)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler('gira_cde.log')
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)

        logger.info('===============================================')
        logger.info('Begin GIRA CDE script')

        # Read config file
        parser = ConfigParser(inline_comment_prefixes=['#'])
        parser.read('./config.ini')
        # REDCap
        redcap_api_endpoint = parser.get('REDCAP', 'LOCAL_REDCAP_URL')
        redcap_api_token = parser.get('REDCAP', 'LOCAL_REDCAP_API_KEY')
        # R4
        r4_api_endpoint = parser.get('R4', 'R4_URL')
        r4_api_token = parser.get('R4', 'R4_API_KEY')
        # Email
        email_host = parser.get('EMAIL', 'SMTP_HOST')
        email_port = parser.get('EMAIL', 'SMTP_PORT')
        email_from = parser.get('EMAIL', 'FROM_ADDR')
        email_to = parser.get('EMAIL', 'TO_ADDRS')
        email_to = [e.strip() for e in email_to.split(';') if e.strip()]  # split emails by ; and get rid of empty
        # OMOP
        omop_instance = parser.get('OMOP', 'DB_NAME')
        logger.info(f'OMOP instance: {omop_instance}')

        # Emailer to notify dev of failures
        emailer = Emailer(email_host, email_port, email_from, email_to)

        # Redcap configuration
        redcap_cde = RedcapCDE(redcap_api_endpoint, redcap_api_token)

        # R4 configuration
        r4 = R4GiraClinVar(r4_api_endpoint, r4_api_token)

        # While we're developing the script, force double check of which projects we're working on
        CHECK_BEFORE_RUNNING = False
        redcap_project_title = redcap_cde.export_project_info()['project_title']
        if CHECK_BEFORE_RUNNING and (input(f'Working on redcap project: {redcap_project_title}. Enter the project title to continue:\n') != redcap_project_title):
            print('Exiting')
            exit()
        r4_project_title = r4.export_project_info()['project_title']
        if CHECK_BEFORE_RUNNING and (input(f'Working on R4 project: {r4_project_title}. Enter the project title to continue:\n') != r4_project_title):
            print('Exiting')
            exit()

        timestamp = datetime.now().isoformat()

        # Get participants still needing CDE
        participant_info = redcap_cde.get_participants_needing_cde(omop_instance)
        if not participant_info:
            logger.info('No participants need CDE')
        else:
            logger.info(f'{len(participant_info)} participants have been collected for CDE')

            # Currently in development. Show what information has been collecetd and verify before continuing to send data out
            if CHECK_BEFORE_RUNNING:
                pprint(participant_info)
                if input('Enter "yes" to continue: ') != 'yes':
                    logger.debug('Exiting script prior to performing CDE.')
                    exit()

            # OMOP connection
            logger.debug('Connecting to OMOP SQL Server')
            sql_engine = omop_cde.sql_server_engine()
            omop = omop_cde.OmopExtractor(sql_engine.connect())

            for p in participant_info:
                record_id = p[RedcapCDE.FIELD_RECORD_ID]
                dob_str = p[RedcapCDE.FIELD_DOB]
                dob_date = date.fromisoformat(dob_str)
                mrn = p[RedcapCDE.FIELD_MRN]
                cde_status = p[RedcapCDE.FIELD_GIRA_CDE_STATUS]
                cde_script_message = p[RedcapCDE.FIELD_GIRA_CDE_SCRIPT_OUTPUT]

                logger.info(f'Starting CDE. CUIMC ID:{record_id}, MRN:{mrn}, DOB:{dob_str}')

                # If there was a previous script message, add a visual separator for new script message
                if cde_script_message:
                    cde_script_message += '===============================\n'

                # Initiate cde_result and keep track of queried information
                cde_result = {
                    RedcapCDE.FIELD_RECORD_ID: record_id,
                    RedcapCDE.FIELD_GIRA_CDE_MRN_QUERIED: mrn,
                    RedcapCDE.FIELD_GIRA_CDE_DOB_QUERIED: dob_str,
                    RedcapCDE.FIELD_GIRA_CDE_OMOP_INSTANCE: omop_instance
                }
                cde_script_message += f"{timestamp}\nmrn:{mrn}\ndob:{dob_str}\ndatabase:{omop_instance}\n"

                # Find the patient info in OMOP
                match: omop_cde.MrnMatch = None
                match, dob_sim = omop.find_closest_patient(mrn, dob_date)

                if not match:
                    # No matching MRNs were found.
                    msg = 'MRN was not found in OMOP database'
                    logger.info(msg)
                    cde_script_message += f'{msg}\n'
                    cde_result[RedcapCDE.FIELD_GIRA_CDE_SCRIPT_OUTPUT] = cde_script_message
                    cde_result[RedcapCDE.FIELD_GIRA_CDE_STATUS] = RedcapCDE.GiraCdeStatus.MRN_NOT_FOUND.value
                    redcap_cde.update_gira_cde(cde_result)
                    continue

                # Check DOB
                cde_result[RedcapCDE.FIELD_EHR_DATE_OF_BIRTH_LOCAL] = match.dob.isoformat()
                if dob_sim != 1:
                    # DOB in REDCap does not match EHR
                    if cde_status == RedcapCDE.GiraCdeStatus.BDMM_PROCEED.value:
                        # Instructed to proceed with CDE despite DOB mismatch
                        msg = 'DOB mismatched, but instructed to proceed'
                        logger.info(msg)
                        cde_script_message += f"{msg}\n"
                    else:
                        msg = 'DOB found in OMOP does not match with REDCap. Review needed.'
                        logger.info(msg)
                        cde_script_message += f'{msg}\n'
                        cde_result[RedcapCDE.FIELD_GIRA_CDE_SCRIPT_OUTPUT] = cde_script_message
                        cde_result[RedcapCDE.FIELD_GIRA_CDE_STATUS] = RedcapCDE.GiraCdeStatus.BDMM_REVIEW_NEEDED.value
                        redcap_cde.update_gira_cde(cde_result)
                        continue

                # OMOP doesn't have names. Copy from REDCap
                cde_result[RedcapCDE.FIELD_EHR_PARTICIPANT_FIRST_NAME_LOCAL] = p[RedcapCDE.FIELD_NAME_FIRST]
                cde_result[RedcapCDE.FIELD_EHR_PARTICIPANT_LAST_NAME_LOCAL] = p[RedcapCDE.FIELD_NAME_LAST]

                msg = f'Extracting for OMOP person_id: {match.omop_person_id}'
                logger.info(msg)
                cde_script_message += f'{msg}\n'

                # Allergies
                allergies_count = omop.count_positive_allergy_tests(match.omop_person_id)
                cde_result[RedcapCDE.FIELD_COUNT_POSITIVE_ALLERGY_LOCAL] = allergies_count
                cde_result[RedcapCDE.FIELD_ALLERGY_TEST_FLAG_LOCAL] = 1 if allergies_count >= 2 else 0

                # Numerical labs
                needs_review = list()
                dbp, sbp, hdl, cho, tri, a1c = omop.extract_gira_labs(match.omop_person_id)

                # systolic blood pressure
                if sbp is not None:
                    sbp_value = sbp.value_as_number
                    cde_result[RedcapCDE.FIELD_SBP_LAB_NAME_LOCAL] = sbp.concept_name
                    cde_result[RedcapCDE.FIELD_SBP_DATE_AT_EVENT_LOCAL] = sbp.measurement_date.isoformat()
                    cde_result[RedcapCDE.FIELD_SBP_MEASUREMENT_CONCEPT_ID_LOCAL] = str(sbp.measurement_concept_id)
                    cde_result[RedcapCDE.FIELD_SBP_VALUE_MOST_RECENT_LOCAL] = sbp_value

                    if sbp_value < 60 or sbp_value > 240:
                        needs_review.append('SBP [60-240]')
                else:
                    cde_result[RedcapCDE.FIELD_SBP_LAB_NAME_LOCAL] = RedcapCDE.MISSING_CONCEPT_NAME
                    cde_result[RedcapCDE.FIELD_SBP_DATE_AT_EVENT_LOCAL] = RedcapCDE.MISSING_DATE
                    cde_result[RedcapCDE.FIELD_SBP_VALUE_MOST_RECENT_LOCAL] = RedcapCDE.MISSING_VALUE

                # diastolic blood pressure
                if dbp is not None:
                    dbp_value = dbp.value_as_number
                    cde_result[RedcapCDE.FIELD_DBP_LAB_NAME_LOCAL] = dbp.concept_name
                    cde_result[RedcapCDE.FIELD_DBP_DATE_AT_EVENT_LOCAL] = dbp.measurement_date.isoformat()
                    cde_result[RedcapCDE.FIELD_DBP_MEASUREMENT_CONCEPT_ID_LOCAL] = str(dbp.measurement_concept_id)
                    cde_result[RedcapCDE.FIELD_DBP_VALUE_MOST_RECENT_LOCAL] = dbp_value

                    if dbp_value < 0 or (sbp is not None and (dbp_value >= sbp_value)):
                        needs_review.append('DBP [0-SBP]')
                else:
                    cde_result[RedcapCDE.FIELD_DBP_LAB_NAME_LOCAL] = RedcapCDE.MISSING_CONCEPT_NAME
                    cde_result[RedcapCDE.FIELD_DBP_DATE_AT_EVENT_LOCAL] = RedcapCDE.MISSING_DATE
                    cde_result[RedcapCDE.FIELD_DBP_VALUE_MOST_RECENT_LOCAL] = RedcapCDE.MISSING_VALUE

                # HDL
                if hdl is not None:
                    hdl_value = hdl.value_as_number
                    cde_result[RedcapCDE.FIELD_HDL_LAB_NAME_LOCAL] = hdl.concept_name
                    cde_result[RedcapCDE.FIELD_HDL_DATE_AT_EVENT_LOCAL] = hdl.measurement_date.isoformat()
                    cde_result[RedcapCDE.FIELD_HDL_MEASUREMENT_CONCEPT_ID_LOCAL] = str(hdl.measurement_concept_id)
                    cde_result[RedcapCDE.FIELD_HDL_VALUE_MOST_RECENT_LOCAL] = hdl_value

                    if hdl_value < 5 or hdl_value > 200:
                        needs_review.append('HDL [5-200]')
                else:
                    cde_result[RedcapCDE.FIELD_HDL_LAB_NAME_LOCAL] = RedcapCDE.MISSING_CONCEPT_NAME
                    cde_result[RedcapCDE.FIELD_HDL_DATE_AT_EVENT_LOCAL] = RedcapCDE.MISSING_DATE
                    cde_result[RedcapCDE.FIELD_HDL_VALUE_MOST_RECENT_LOCAL] = RedcapCDE.MISSING_VALUE

                # Total Cholesterol
                if cho is not None:
                    cho_value = cho.value_as_number
                    cde_result[RedcapCDE.FIELD_TOTALCHOLEST_LAB_NAME_LOCAL] = cho.concept_name
                    cde_result[RedcapCDE.FIELD_TOTALCHOLEST_DATE_AT_EVENT_LOCAL] = cho.measurement_date.isoformat()
                    cde_result[RedcapCDE.FIELD_TOTALCHOLEST_MEASUREMENT_CONCEPT_ID_LOCAL] = str(cho.measurement_concept_id)
                    cde_result[RedcapCDE.FIELD_TOTALCHOLEST_VALUE_MOST_RECENT_LOCAL] = cho_value

                    if cho_value < 50 or cho_value > 1000:
                        needs_review.append('total cholesterol [50-1000]')
                else:
                    cde_result[RedcapCDE.FIELD_TOTALCHOLEST_LAB_NAME_LOCAL] = RedcapCDE.MISSING_CONCEPT_NAME
                    cde_result[RedcapCDE.FIELD_TOTALCHOLEST_DATE_AT_EVENT_LOCAL] = RedcapCDE.MISSING_DATE
                    cde_result[RedcapCDE.FIELD_TOTALCHOLEST_VALUE_MOST_RECENT_LOCAL] = RedcapCDE.MISSING_VALUE

                # Triglyceride
                if tri is not None:
                    cde_result[RedcapCDE.FIELD_TRIGLYCERIDE_LAB_NAME_LOCAL] = tri.concept_name
                    cde_result[RedcapCDE.FIELD_TRIGLYCERIDE_DATE_AT_EVENT_LOCAL] = tri.measurement_date.isoformat()
                    cde_result[RedcapCDE.FIELD_TRIGLYCERIDE_MEASUREMENT_CONCEPT_ID_LOCAL] = str(tri.measurement_concept_id)
                    cde_result[RedcapCDE.FIELD_TRIGLYCERIDE_VALUE_MOST_RECENT_LOCAL] = tri.value_as_number
                else:
                    cde_result[RedcapCDE.FIELD_TRIGLYCERIDE_LAB_NAME_LOCAL] = RedcapCDE.MISSING_CONCEPT_NAME
                    cde_result[RedcapCDE.FIELD_TRIGLYCERIDE_DATE_AT_EVENT_LOCAL] = RedcapCDE.MISSING_DATE
                    cde_result[RedcapCDE.FIELD_TRIGLYCERIDE_VALUE_MOST_RECENT_LOCAL] = RedcapCDE.MISSING_VALUE

                # A1c
                if a1c is not None:
                    a1c_value = a1c.value_as_number
                    cde_result[RedcapCDE.FIELD_A1C_LAB_NAME_LOCAL] = a1c.concept_name
                    cde_result[RedcapCDE.FIELD_A1C_DATE_AT_EVENT_LOCAL] = a1c.measurement_date.isoformat()
                    cde_result[RedcapCDE.FIELD_A1C_MEASUREMENT_CONCEPT_ID_LOCAL] = str(a1c.measurement_concept_id)
                    cde_result[RedcapCDE.FIELD_A1C_VALUE_MOST_RECENT_LOCAL] = a1c_value

                    if a1c_value < 2 or a1c_value > 20:
                        needs_review.append('a1c [2-20]')
                else:
                    cde_result[RedcapCDE.FIELD_A1C_LAB_NAME_LOCAL] = RedcapCDE.MISSING_CONCEPT_NAME
                    cde_result[RedcapCDE.FIELD_A1C_DATE_AT_EVENT_LOCAL] = RedcapCDE.MISSING_DATE
                    cde_result[RedcapCDE.FIELD_A1C_VALUE_MOST_RECENT_LOCAL] = RedcapCDE.MISSING_VALUE

                # Wheeze 1
                wheeze_events = omop.wheeze_events(match.omop_person_id)
                cde_result[RedcapCDE.FIELD_WHEEZING_FLAG_LOCAL] = 0
                event_age = RedcapCDE.MISSING_VALUE
                if len(wheeze_events) >= 1:
                    event_age = wheeze_events[0].age
                cde_result[RedcapCDE.FIELD_AGE_AT_FIRST_WHEEZE_EVENT_LOCAL] = event_age

                # Wheeze 2
                event_age = RedcapCDE.MISSING_VALUE
                if len(wheeze_events) >= 2:
                    event_age = wheeze_events[1].age
                    cde_result[RedcapCDE.FIELD_WHEEZING_FLAG_LOCAL] = 1
                cde_result[RedcapCDE.FIELD_AGE_AT_SECOND_WHEEZE_EVENT_LOCAL] = event_age

                # Eczema 1
                eczema_events = omop.eczema_events(match.omop_person_id)
                cde_result[RedcapCDE.FIELD_ECZEMA_FLAG_LOCAL] = 0
                event_age = RedcapCDE.MISSING_VALUE
                if len(eczema_events) >= 1:
                    event_age = eczema_events[0].age
                cde_result[RedcapCDE.FIELD_AGE_AT_FIRST_ECZEMA_EVENT_LOCAL] = event_age

                # Eczema 2
                event_age = RedcapCDE.MISSING_VALUE
                if len(eczema_events) >= 2:
                    event_age = eczema_events[1]
                    cde_result[RedcapCDE.FIELD_ECZEMA_FLAG_LOCAL] = 1
                cde_result[RedcapCDE.FIELD_AGE_AT_SECOND_ECZEMA_EVENT_LOCAL] = event_age

                msg = 'CDE complete'
                logger.info(msg)
                cde_script_message += f'{msg}\n'

                # Check which labs need review
                if needs_review:
                    msg = f'The following labs need review (lab [range]): {", ".join(needs_review)}'
                    logger.info(msg)
                    cde_script_message += f'{msg}\n'
                    cde_result[RedcapCDE.FIELD_GIRA_CDE_REVIEW_STATUS] = RedcapCDE.GiraReviewStatus.NEEDED.value
                    cde_result[RedcapCDE.FIELD_GIRA_CLINICAL_VARIABLES_LOCAL_COMPLETE] = renums.Complete.INCOMPLETE.value
                else:
                    msg = 'No review needed for lab measurements'
                    logger.debug(msg)
                    cde_script_message += f'{msg}\n'
                    cde_result[RedcapCDE.FIELD_GIRA_CDE_REVIEW_STATUS] = RedcapCDE.GiraReviewStatus.NOT_NEEDED.value
                    # Mark this instrument as incomplete (until uploaded to R4)
                    cde_result[RedcapCDE.FIELD_GIRA_CLINICAL_VARIABLES_LOCAL_COMPLETE] = renums.Complete.INCOMPLETE.value

                # Update local GIRA CDE instrument
                cde_result[RedcapCDE.FIELD_GIRA_CDE_STATUS] = RedcapCDE.GiraCdeStatus.COMPLETED.value
                cde_result[RedcapCDE.FIELD_GIRA_CDE_SCRIPT_OUTPUT] = cde_script_message
                logger.debug(cde_result)
                update_result = redcap_cde.update_gira_cde(cde_result)

                if update_result['count'] != 1:
                    logger.error(f'Local CDE not updated correctly for participant {record_id}. Update result: {update_result}')
                else:
                    logger.info('Local GIRA CDE instrument updated')

            logger.info('Finished CDE')


        # Get participants with CDE needing upload to R4
        participant_info = redcap_cde.get_participants_to_upload_r4()
        if not participant_info:
            logger.info('No participants with CDE needing upload to R4')
        else:
            logger.info(f'{len(participant_info)} participants have been collected for R4 upload')

            # Currently in development. Show what information has been collecetd and verify before continuing to send data out
            if CHECK_BEFORE_RUNNING:
                pprint(participant_info)
                if input('Enter "yes" to continue: ') != 'yes':
                    logger.debug('Exiting script prior to performing R4 upload.')
                    exit()

            for p in participant_info:
                record_id = p[RedcapCDE.FIELD_RECORD_ID]
                r4_record_id = p[RedcapCDE.FIELD_R4_RECORD_ID]
                r4_script_message = p[RedcapCDE.FIELD_GIRA_CDE_R4_SCRIPT_OUTPUT]

                logger.info(f'Starting R4 Upload. CUIMC ID:{record_id}, R4 Record ID:{r4_record_id}')

                # If there was a previous script message, add a visual separator for new script message
                if r4_script_message:
                    r4_script_message += '===============================\n'
                r4_script_message += f"{timestamp}\nUploading to R4\n"

                # Initiate cde_result and gira clinical variable record
                cde_result = {
                    RedcapCDE.FIELD_RECORD_ID: record_id
                }
                gira_cv_record = {
                    RedcapCDE.FIELD_R4_RECORD_ID: r4_record_id,
                    # RedcapCDE.FIELD_RECORD_ID: record_id,  # This is only used for testing purposes when the target project is a clone of our local project
                    R4GiraClinVar.FIELD_GIRA_CLINICAL_VARIABLES_COMPLETE: renums.Complete.COMPLETE.value
                }

                # Copy over all data fields in GIRA Clinical Variables Instrument
                # All data fields have a copy in the GIRA Clinical Variables local instrument with a "_local" suffix appended
                for f in R4GiraClinVar.DATA_FIELDS:
                    gira_cv_record[f] = p[f + RedcapCDE.LOCAL_FIELD_SUFFIX]

                # Import to R4
                update_result = r4.import_records([gira_cv_record])
                if update_result['count'] != 1:
                    logger.error(f'R4 not updated correctly for participant {record_id}. Update result: {update_result}')
                    r4_script_message += 'Upload to R4 failed\n'
                    cde_result[RedcapCDE.FIELD_GIRA_CDE_R4_SCRIPT_OUTPUT] = r4_script_message
                else:
                    logger.info('R4 GIRA CDE instrument updated')
                    r4_script_message += 'Upload to R4 succeeded\n'
                    cde_result[RedcapCDE.FIELD_GIRA_CDE_R4_SCRIPT_OUTPUT] = r4_script_message
                    cde_result[RedcapCDE.FIELD_GIRA_CLINICAL_VARIABLES_LOCAL_COMPLETE] = renums.Complete.COMPLETE.value

                # Update local instrument with status
                update_result = redcap_cde.update_gira_cde(cde_result)
                if update_result['count'] != 1:
                    logger.error(f'Local CDE not updated correctly for participant {record_id}. Update result: {update_result}')
                else:
                    logger.info('Local GIRA CDE instrument updated')

        logger.info('Script completed normally')

    except Exception as e:
        logger.exception(e)
    finally:
        if error_handler.fired:
            emailer.sendmail('GIRA CDE error', 'An issue occurred in the GIRA CDE script. Please check the logs.')
