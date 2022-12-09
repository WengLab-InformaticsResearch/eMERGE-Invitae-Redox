from urllib.parse import urljoin
import logging

from redcap import Project

logger = logging.getLogger(__name__)

class R4GiraClinVar(Project):
    # REDCap variable names
    # IDs
    FIELD_RECORD_ID = 'record_id'  # Record ID in R4
    # GIRA CDE data fields
    FIELD_EHR_PARTICIPANT_FIRST_NAME = 'ehr_participant_first_name'
    FIELD_EHR_PARTICIPANT_LAST_NAME = 'ehr_participant_last_name'
    FIELD_EHR_DATE_OF_BIRTH = 'ehr_date_of_birth'
    FIELD_COUNT_POSITIVE_ALLERGY = 'count_positive_allergy'
    FIELD_ALLERGY_TEST_FLAG = 'allergy_test_flag'
    FIELD_HDL_LAB_NAME = 'hdl_lab_name'
    FIELD_HDL_DATE_AT_EVENT = 'hdl_date_at_event'
    FIELD_HDL_MEASUREMENT_CONCEPT_ID = 'hdl_measurement_concept_id'
    FIELD_HDL_VALUE_MOST_RECENT = 'hdl_value_most_recent'
    FIELD_TOTALCHOLEST_LAB_NAME = 'totalcholest_lab_name'
    FIELD_TOTALCHOLEST_DATE_AT_EVENT = 'totalcholest_date_at_event'
    FIELD_TOTALCHOLEST_MEASUREMENT_CONCEPT_ID = 'totalcholest_measurement_concept_id'
    FIELD_TOTALCHOLEST_VALUE_MOST_RECENT = 'totalcholest_value_most_recent'
    FIELD_TRIGLYCERIDE_LAB_NAME = 'triglyceride_lab_name'
    FIELD_TRIGLYCERIDE_DATE_AT_EVENT = 'triglyceride_date_at_event'
    FIELD_TRIGLYCERIDE_MEASUREMENT_CONCEPT_ID = 'triglyceride_measurement_concept_id'
    FIELD_TRIGLYCERIDE_VALUE_MOST_RECENT = 'triglyceride_value_most_recent'
    FIELD_A1C_LAB_NAME = 'a1c_lab_name'
    FIELD_A1C_DATE_AT_EVENT = 'a1c_date_at_event'
    FIELD_A1C_MEASUREMENT_CONCEPT_ID = 'a1c_measurement_concept_id'
    FIELD_A1C_VALUE_MOST_RECENT = 'a1c_value_most_recent'
    FIELD_DBP_LAB_NAME = 'dbp_lab_name'
    FIELD_DBP_DATE_AT_EVENT = 'dbp_date_at_event'
    FIELD_DBP_MEASUREMENT_CONCEPT_ID = 'dbp_measurement_concept_id'
    FIELD_DBP_VALUE_MOST_RECENT = 'dbp_value_most_recent'
    FIELD_SBP_LAB_NAME = 'sbp_lab_name'
    FIELD_SBP_DATE_AT_EVENT = 'sbp_date_at_event'
    FIELD_SBP_MEASUREMENT_CONCEPT_ID = 'sbp_measurement_concept_id'
    FIELD_SBP_VALUE_MOST_RECENT = 'sbp_value_most_recent'
    FIELD_AGE_AT_FIRST_WHEEZE_EVENT = 'age_at_first_wheeze_event'
    FIELD_AGE_AT_SECOND_WHEEZE_EVENT = 'age_at_second_wheeze_event'
    FIELD_WHEEZING_FLAG = 'wheezing_flag'
    FIELD_AGE_AT_FIRST_ECZEMA_EVENT = 'age_at_first_eczema_event'
    FIELD_AGE_AT_SECOND_ECZEMA_EVENT = 'age_at_second_eczema_event'
    FIELD_ECZEMA_FLAG = 'eczema_flag'
    # Instrument completion status
    FIELD_GIRA_CLINICAL_VARIABLES_COMPLETE = 'gira_clinical_variables_complete'

    DATA_FIELDS = [
        FIELD_EHR_PARTICIPANT_FIRST_NAME,
        FIELD_EHR_PARTICIPANT_LAST_NAME,
        FIELD_EHR_DATE_OF_BIRTH,
        FIELD_COUNT_POSITIVE_ALLERGY,
        FIELD_ALLERGY_TEST_FLAG,
        FIELD_HDL_LAB_NAME,
        FIELD_HDL_DATE_AT_EVENT,
        FIELD_HDL_MEASUREMENT_CONCEPT_ID,
        FIELD_HDL_VALUE_MOST_RECENT,
        FIELD_TOTALCHOLEST_LAB_NAME,
        FIELD_TOTALCHOLEST_DATE_AT_EVENT,
        FIELD_TOTALCHOLEST_MEASUREMENT_CONCEPT_ID,
        FIELD_TOTALCHOLEST_VALUE_MOST_RECENT,
        FIELD_TRIGLYCERIDE_LAB_NAME,
        FIELD_TRIGLYCERIDE_DATE_AT_EVENT,
        FIELD_TRIGLYCERIDE_MEASUREMENT_CONCEPT_ID,
        FIELD_TRIGLYCERIDE_VALUE_MOST_RECENT,
        FIELD_A1C_LAB_NAME,
        FIELD_A1C_DATE_AT_EVENT,
        FIELD_A1C_MEASUREMENT_CONCEPT_ID,
        FIELD_A1C_VALUE_MOST_RECENT,
        FIELD_DBP_LAB_NAME,
        FIELD_DBP_DATE_AT_EVENT,
        FIELD_DBP_MEASUREMENT_CONCEPT_ID,
        FIELD_DBP_VALUE_MOST_RECENT,
        FIELD_SBP_LAB_NAME,
        FIELD_SBP_DATE_AT_EVENT,
        FIELD_SBP_MEASUREMENT_CONCEPT_ID,
        FIELD_SBP_VALUE_MOST_RECENT,
        FIELD_AGE_AT_FIRST_WHEEZE_EVENT,
        FIELD_AGE_AT_SECOND_WHEEZE_EVENT,
        FIELD_WHEEZING_FLAG,
        FIELD_AGE_AT_FIRST_ECZEMA_EVENT,
        FIELD_AGE_AT_SECOND_ECZEMA_EVENT,
        FIELD_ECZEMA_FLAG
    ]

    # Missing data values
    MISSING_DATA = '!'
    MISSING_VALUE = -9
    MISSING_DATE = '1900-01-01'
    MISSING_CONCEPT_NAME = 'N/A'

    def __init__(self, endpoint, api_token):
        self.endpoint = endpoint
        self.api_token = api_token

        # PyCap expects endpoint to end with '/'
        if self.endpoint[-1] != '/':
            self.endpoint += '/'
        super().__init__(self.endpoint, self.api_token)
