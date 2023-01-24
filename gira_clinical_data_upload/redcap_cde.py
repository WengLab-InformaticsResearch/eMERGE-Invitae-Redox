import logging
from enum import Enum

from redcap import Project

import redcap_enums as renums

logger = logging.getLogger(__name__)

class RedcapCDE(Project):
    # REDCap variable names
    # IDs
    FIELD_RECORD_ID = 'cuimc_id'  # In CUIMC local REDCap, cuimc_id is the primary Record ID
    FIELD_R4_RECORD_ID = 'record_id'  # Record ID in R4
    FIELD_LAB_ID = 'participant_lab_id'
    FIELD_MRN = 'mrn'
    # Participant Info
    FIELD_DOB = 'participant_date_of_birth'
    FIELD_NAME_FIRST = 'participant_first_name'
    FIELD_NAME_MIDDLE = 'participant_middle_name'
    FIELD_NAME_LAST = 'last_name'
    FIELD_SEX = 'sex_at_birth'
    FIELD_AGE = 'age'
    # Participation status
    FIELD_CONSENT_DATE = 'date_consent_cu_2'
    FIELD_CONSENT_PP_DATE = 'date_consent_cu_2_pp'
    FIELD_WITHDRAWAL = 'participant_withdrawal'
    # GIRA CDE Local instrument - script fields
    FIELD_GIRA_CDE_SCRIPT_OUTPUT = 'gira_cde_script_output'
    FIELD_GIRA_CDE_OMOP_INSTANCE = 'gira_cde_omop_instance'
    FIELD_GIRA_CDE_MRN_QUERIED = 'gira_cde_mrn_queried'
    FIELD_GIRA_CDE_DOB_QUERIED = 'gira_cde_dob_queried'
    FIELD_GIRA_CDE_STATUS = 'gira_cde_status'
    FIELD_GIRA_CDE_REVIEW_STATUS = 'gira_cde_review_status'
    FIELD_GIRA_CDE_R4_SCRIPT_OUTPUT = 'gira_cde_r4_script_output'
    # GIRA CDE Local instrument - data fields
    FIELD_EHR_PARTICIPANT_FIRST_NAME_LOCAL = 'ehr_participant_first_name_local'
    FIELD_EHR_PARTICIPANT_LAST_NAME_LOCAL = 'ehr_participant_last_name_local'
    FIELD_EHR_DATE_OF_BIRTH_LOCAL = 'ehr_date_of_birth_local'
    FIELD_COUNT_POSITIVE_ALLERGY_LOCAL = 'count_positive_allergy_local'
    FIELD_ALLERGY_TEST_FLAG_LOCAL = 'allergy_test_flag_local'
    FIELD_HDL_LAB_NAME_LOCAL = 'hdl_lab_name_local'
    FIELD_HDL_DATE_AT_EVENT_LOCAL = 'hdl_date_at_event_local'
    FIELD_HDL_MEASUREMENT_CONCEPT_ID_LOCAL = 'hdl_measurement_concept_id_local'
    FIELD_HDL_VALUE_MOST_RECENT_LOCAL = 'hdl_value_most_recent_local'
    FIELD_TOTALCHOLEST_LAB_NAME_LOCAL = 'totalcholest_lab_name_local'
    FIELD_TOTALCHOLEST_DATE_AT_EVENT_LOCAL = 'totalcholest_date_at_event_local'
    FIELD_TOTALCHOLEST_MEASUREMENT_CONCEPT_ID_LOCAL = 'totalcholest_measurement_concept_id_local'
    FIELD_TOTALCHOLEST_VALUE_MOST_RECENT_LOCAL = 'totalcholest_value_most_recent_local'
    FIELD_TRIGLYCERIDE_LAB_NAME_LOCAL = 'triglyceride_lab_name_local'
    FIELD_TRIGLYCERIDE_DATE_AT_EVENT_LOCAL = 'triglyceride_date_at_event_local'
    FIELD_TRIGLYCERIDE_MEASUREMENT_CONCEPT_ID_LOCAL = 'triglyceride_measurement_concept_id_local'
    FIELD_TRIGLYCERIDE_VALUE_MOST_RECENT_LOCAL = 'triglyceride_value_most_recent_local'
    FIELD_A1C_LAB_NAME_LOCAL = 'a1c_lab_name_local'
    FIELD_A1C_DATE_AT_EVENT_LOCAL = 'a1c_date_at_event_local'
    FIELD_A1C_MEASUREMENT_CONCEPT_ID_LOCAL = 'a1c_measurement_concept_id_local'
    FIELD_A1C_VALUE_MOST_RECENT_LOCAL = 'a1c_value_most_recent_local'
    FIELD_DBP_LAB_NAME_LOCAL = 'dbp_lab_name_local'
    FIELD_DBP_DATE_AT_EVENT_LOCAL = 'dbp_date_at_event_local'
    FIELD_DBP_MEASUREMENT_CONCEPT_ID_LOCAL = 'dbp_measurement_concept_id_local'
    FIELD_DBP_VALUE_MOST_RECENT_LOCAL = 'dbp_value_most_recent_local'
    FIELD_SBP_LAB_NAME_LOCAL = 'sbp_lab_name_local'
    FIELD_SBP_DATE_AT_EVENT_LOCAL = 'sbp_date_at_event_local'
    FIELD_SBP_MEASUREMENT_CONCEPT_ID_LOCAL = 'sbp_measurement_concept_id_local'
    FIELD_SBP_VALUE_MOST_RECENT_LOCAL = 'sbp_value_most_recent_local'
    FIELD_AGE_AT_FIRST_WHEEZE_EVENT_LOCAL = 'age_at_first_wheeze_event_local'
    FIELD_AGE_AT_SECOND_WHEEZE_EVENT_LOCAL = 'age_at_second_wheeze_event_local'
    FIELD_WHEEZING_FLAG_LOCAL = 'wheezing_flag_local'
    FIELD_AGE_AT_FIRST_ECZEMA_EVENT_LOCAL = 'age_at_first_eczema_event_local'
    FIELD_AGE_AT_SECOND_ECZEMA_EVENT_LOCAL = 'age_at_second_eczema_event_local'
    FIELD_ECZEMA_FLAG_LOCAL = 'eczema_flag_local'
    # Instrument completion status
    FIELD_GIRA_CLINICAL_VARIABLES_LOCAL_COMPLETE = 'gira_clinical_variables_local_complete'

    # Suffix appended to field names of the main GIRA Clinical Variables instrument
    LOCAL_FIELD_SUFFIX ='_local'

    # Fields needed to determine participation status
    PARTICIPATION_FIELDS = [FIELD_AGE,
                            FIELD_CONSENT_DATE,
                            FIELD_CONSENT_PP_DATE,
                            FIELD_WITHDRAWAL]

    # Clinical variable fields
    DATA_FIELDS = [
        FIELD_EHR_PARTICIPANT_FIRST_NAME_LOCAL,
        FIELD_EHR_PARTICIPANT_LAST_NAME_LOCAL,
        FIELD_EHR_DATE_OF_BIRTH_LOCAL,
        FIELD_COUNT_POSITIVE_ALLERGY_LOCAL,
        FIELD_ALLERGY_TEST_FLAG_LOCAL,
        FIELD_HDL_LAB_NAME_LOCAL,
        FIELD_HDL_DATE_AT_EVENT_LOCAL,
        FIELD_HDL_MEASUREMENT_CONCEPT_ID_LOCAL,
        FIELD_HDL_VALUE_MOST_RECENT_LOCAL,
        FIELD_TOTALCHOLEST_LAB_NAME_LOCAL,
        FIELD_TOTALCHOLEST_DATE_AT_EVENT_LOCAL,
        FIELD_TOTALCHOLEST_MEASUREMENT_CONCEPT_ID_LOCAL,
        FIELD_TOTALCHOLEST_VALUE_MOST_RECENT_LOCAL,
        FIELD_TRIGLYCERIDE_LAB_NAME_LOCAL,
        FIELD_TRIGLYCERIDE_DATE_AT_EVENT_LOCAL,
        FIELD_TRIGLYCERIDE_MEASUREMENT_CONCEPT_ID_LOCAL,
        FIELD_TRIGLYCERIDE_VALUE_MOST_RECENT_LOCAL,
        FIELD_A1C_LAB_NAME_LOCAL,
        FIELD_A1C_DATE_AT_EVENT_LOCAL,
        FIELD_A1C_MEASUREMENT_CONCEPT_ID_LOCAL,
        FIELD_A1C_VALUE_MOST_RECENT_LOCAL,
        FIELD_DBP_LAB_NAME_LOCAL,
        FIELD_DBP_DATE_AT_EVENT_LOCAL,
        FIELD_DBP_MEASUREMENT_CONCEPT_ID_LOCAL,
        FIELD_DBP_VALUE_MOST_RECENT_LOCAL,
        FIELD_SBP_LAB_NAME_LOCAL,
        FIELD_SBP_DATE_AT_EVENT_LOCAL,
        FIELD_SBP_MEASUREMENT_CONCEPT_ID_LOCAL,
        FIELD_SBP_VALUE_MOST_RECENT_LOCAL,
        FIELD_AGE_AT_FIRST_WHEEZE_EVENT_LOCAL,
        FIELD_AGE_AT_SECOND_WHEEZE_EVENT_LOCAL,
        FIELD_WHEEZING_FLAG_LOCAL,
        FIELD_AGE_AT_FIRST_ECZEMA_EVENT_LOCAL,
        FIELD_AGE_AT_SECOND_ECZEMA_EVENT_LOCAL,
        FIELD_ECZEMA_FLAG_LOCAL
    ]

    # Missing data values
    MISSING_DATA = '!'
    MISSING_VALUE = -9
    MISSING_DATE = '1900-01-01'
    MISSING_CONCEPT_NAME = 'N/A'

    class GiraCdeStatus(Enum):
        COMPLETED = '1'
        # Birthday Mismatch (BDMM)
        BDMM_REVIEW_NEEDED = '2'
        BDMM_DO_NOT_PROCEED = '3'
        BDMM_PROCEED = '4'
        # Other
        MRN_NOT_FOUND = '5'

    class GiraReviewStatus(Enum):
        NOT_NEEDED = '1'
        NEEDED = '2'
        REVIEWED = '3'

    def __init__(self, endpoint, api_token):
        self.endpoint = endpoint
        self.api_token = api_token

        # PyCap expects endpoint to end with '/'
        if self.endpoint[-1] != '/':
            self.endpoint += '/'

        super().__init__(self.endpoint, self.api_token)

    @staticmethod
    def check_participation_status(r):
        ''' Checks participant's records to see if they're participating:
        1) fully consented (by checking consent signature dates is not empty)
        2) not withdrawn

        Params
        ------
        r - records

        Returns
        -------
        True - participant
        False - not fully consented or withdrawn
        '''
        # Check if participant has withdrawn
        if r[RedcapCDE.FIELD_WITHDRAWAL] == renums.YesNo.YES.value:
            logger.debug('Participant withdrawn')
            return False

        # For adult participant, check consent date (recruiter signature)
        # For child participant, check parent permission date (recruiter signature)
        try:
            age = r[RedcapCDE.FIELD_AGE]
            if not age:
                # Empty age. Participant likely didn't complete consent.
                logger.debug('Age is emtpy')
                return False
            age = int(age)
        except ValueError:
            logger.error(f'Age is not a number: {age}')
            return False
        if age >= 18 and not r[RedcapCDE.FIELD_CONSENT_DATE]:
            logger.debug('Adult participant, no consent')
            return False
        if age < 18 and not r[RedcapCDE.FIELD_CONSENT_PP_DATE]:
            logger.debug('Child participant, no parent consent')
            return False

        # Participant considered as still participating
        return True

    def get_participants_needing_cde(self, omop_instance):
        '''
        Eligible: 1) fully consented, 2) not withdrawn

        Params
        ------
        omop_instance: str - name of OMOP database to be queried

        Return
        ------
        List of participant information
        '''
        # Specify which forms and fields needed from the record export
        fields = [RedcapCDE.FIELD_RECORD_ID, RedcapCDE.FIELD_R4_RECORD_ID,
                  RedcapCDE.FIELD_DOB, RedcapCDE.FIELD_MRN,
                  RedcapCDE.FIELD_NAME_FIRST, RedcapCDE.FIELD_NAME_LAST,
                  RedcapCDE.FIELD_GIRA_CDE_SCRIPT_OUTPUT,  RedcapCDE.FIELD_GIRA_CDE_STATUS,
                  RedcapCDE.FIELD_GIRA_CDE_MRN_QUERIED, RedcapCDE.FIELD_GIRA_CDE_OMOP_INSTANCE,
                  RedcapCDE.FIELD_GIRA_CDE_DOB_QUERIED] + RedcapCDE.PARTICIPATION_FIELDS

        participant_info = []
        records = self.export_records(fields=fields)
        for r in records:
            logger.debug(f'Checking if {r[RedcapCDE.FIELD_RECORD_ID]} needs CDE')

            participating = RedcapCDE.check_participation_status(r)
            if not participating:
                logger.debug('Skipping unconsented / withdrawn participant')
                continue

            # If MRN or DOB are empty, skip this participant
            dob = r[RedcapCDE.FIELD_DOB].strip()
            mrn = r[RedcapCDE.FIELD_MRN].strip()
            if not dob or not mrn:
                logger.info("Participant's MRN or DOB not entered yet.")
                continue

            # If CDE has never been run before, add this participant
            cde_status = r[RedcapCDE.FIELD_GIRA_CDE_STATUS]
            if not cde_status:
                logger.debug('CDE never performed before for this participant')
                participant_info.append(r)
                continue

            # Do not perform CDE again if CDE previously completed
            if cde_status == RedcapCDE.GiraCdeStatus.COMPLETED.value:
                logger.debug('Skipping participant, GIRA CDE already performed')
                continue

            # For all other previous CDE statuses, if we're querying a new OMOP instance now, proceed with CDE
            if omop_instance > r[RedcapCDE.FIELD_GIRA_CDE_OMOP_INSTANCE]:
                logger.info(f'OMOP updated. Partcipant {r[RedcapCDE.FIELD_RECORD_ID]} needs CDE')
                participant_info.append(r)
                continue

            # For previous CDE statuses where DOB mismatched, proceed with CDE only if DOB updated or approved to            
            dob_prev = r[RedcapCDE.FIELD_GIRA_CDE_DOB_QUERIED]
            if cde_status == RedcapCDE.GiraCdeStatus.BDMM_REVIEW_NEEDED.value:
                if dob != dob_prev:
                    logger.debug('Previous DOB mismatched, but DOB has been updated. Proceed.')
                    participant_info.append(r)
                    continue
                else:
                    logger.debug('Skipping participant, need to review MRN/DOB mismatch')
                    continue
            elif cde_status == RedcapCDE.GiraCdeStatus.BDMM_DO_NOT_PROCEED.value:
                if dob != dob_prev:
                    logger.debug('Previous DOB mismatched, but DOB has been updated. Proceed.')
                    participant_info.append(r)
                    continue
                else:
                    logger.debug('Skipping participant, MRN/DOB mismatch, do not proceed')
                    continue
            elif cde_status == RedcapCDE.GiraCdeStatus.BDMM_PROCEED.value:
                logger.debug('DOB mismatched, but approved to proceed with CDE')
                participant_info.append(r)
                continue
            # If MRN previously not found, only perform CDE if MRN has been updated or OMOP database updated
            elif cde_status == RedcapCDE.GiraCdeStatus.MRN_NOT_FOUND.value:
                mrn_prev = r[RedcapCDE.FIELD_GIRA_CDE_MRN_QUERIED]                
                if len(mrn.strip()) > 0 and mrn != mrn_prev:
                    logger.debug("MRN has been updated. Perform CDE again for this participant")
                    participant_info.append(r)
                    continue
                else:
                    logger.debug("Skipping participant, participant's MRN was not found previously, and no change in MRN.")
                    continue

            # We shouldn't get here. Do not process this participant
            logger.error(f'Unhandled condition for partcipant {r[RedcapCDE.FIELD_RECORD_ID]}')

        return participant_info

    def update_gira_cde(self, records):
        if not records:
            return 0

        if type(records) is dict:
            records = [records]

        return self.import_records(records)

    def get_participants_to_upload_r4(self):
        '''
        Eligible: 1) fully consented, 2) not withdrawn, 3) clinical data already extracted from OMOP,
        4) clinical data does not need review or has already been reviewed, 5) not already uploaded

        Return
        ------
        List of participant information
        '''
        # Specify which forms and fields needed from the record export
        fields = [
            RedcapCDE.FIELD_RECORD_ID,
            RedcapCDE.FIELD_R4_RECORD_ID,
            RedcapCDE.FIELD_GIRA_CDE_STATUS,
            RedcapCDE.FIELD_GIRA_CDE_REVIEW_STATUS,
            RedcapCDE.FIELD_GIRA_CDE_R4_SCRIPT_OUTPUT,
            RedcapCDE.FIELD_GIRA_CLINICAL_VARIABLES_LOCAL_COMPLETE,
        ] + RedcapCDE.DATA_FIELDS + \
            RedcapCDE.PARTICIPATION_FIELDS

        participant_info = []
        records = self.export_records(fields=fields)
        for r in records:
            logger.debug(f'Checking if {r[RedcapCDE.FIELD_RECORD_ID]} needs upload clinical data to R4')

            participating = RedcapCDE.check_participation_status(r)
            cde_status = r[RedcapCDE.FIELD_GIRA_CDE_STATUS]
            review_status = r[RedcapCDE.FIELD_GIRA_CDE_REVIEW_STATUS]
            completion_status = r[RedcapCDE.FIELD_GIRA_CLINICAL_VARIABLES_LOCAL_COMPLETE]

            if not participating:
                logger.debug('Skipping participant: unconsented / withdrawn')
            elif cde_status != RedcapCDE.GiraCdeStatus.COMPLETED.value:
                logger.debug('Skipping participant: CDE not completed yet')
            elif completion_status == renums.Complete.COMPLETE.value:
                logger.debug('Skipping participant: upload already completed')
            elif review_status == RedcapCDE.GiraReviewStatus.NOT_NEEDED.value:
                logger.debug('Review not needed. Adding participant info to be uploaded to R4')
                participant_info.append(r)
            elif review_status == RedcapCDE.GiraReviewStatus.NOT_NEEDED.value:
                logger.debug('Manual review completed. Adding participant info to be uploaded to R4')
                participant_info.append(r)
            else:
                logger.error(f'Unexpected R4 upload status encountered. Participating: {participating}; CDE status: {cde_status}; '
                             f'review status: {review_status}; completion status: {completion_status}')

        return participant_info
