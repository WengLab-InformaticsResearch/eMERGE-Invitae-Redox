from urllib.parse import urljoin
import json
import logging
from enum import Enum
from datetime import date
import re

import requests
from redcap import Project

logger = logging.getLogger(__name__)

class Redcap:
    _FORM_INVITAE_ORDER = 'specimen_reminders'

    # REDCap variable names
    # IDs
    FIELD_RECORD_ID = 'cuimc_id'  # In CUIMC local REDCap, cuimc_id is the primary Record ID
    FIELD_LAB_ID = 'participant_lab_id'
    # Participant Info
    FIELD_DOB = 'participant_date_of_birth'
    FIELD_NAME_FIRST = 'participant_first_name'
    FIELD_NAME_MIDDLE = 'participant_middle_name'
    FIELD_NAME_LAST = 'last_name'
    FIELD_SEX = 'sex_at_birth'
    FIELD_AGE = 'age'
    FIELD_RACE = 'race_at_enrollment'
    # Invitae Order
    FIELD_SAMPLE_REPLACE = 'sp_invitae_replace'
    FIELD_SAMPLE_RECEIVED = 'sp_invitae_yn'
    FIELD_ORDER_READY = 'sp_invitae_redox_order'
    FIELD_ORDER_ID = 'sp_invitae_redox_order_id'
    FIELD_ORDER_DATE = 'sp_invitae_redox_order_date'
    FIELD_ORDER_STATUS = 'sp_invitae_redox_order_status'
    FIELD_ORDER_FORM_COMPLETE = 'sp_invitae_ordering_complete'

    # Baseline Survey: Personal Health History checkbox fields
    FIELD_BPHH_HYPERTENSION = 'high_blood_pressure_hypert'
    FIELD_BPHH_HYPERLIPID = 'high_cholesterol_hyperlipi'
    FIELD_BPHH_T1DM = 'type_1_diabetes'
    FIELD_BPHH_T2DM = 'type_2_diabetes'
    FIELD_BPHH_KD = 'kidney_disease'
    FIELD_BPHH_ASTHMA = 'asthma'
    FIELD_BPHH_OBESITY = 'obesity'
    FIELD_BPHH_SLEEPAPNEA = 'sleep_apnea'
    FIELD_BPHH_CHD = 'coronary_heart_disease'
    FIELD_BPHH_HF = 'heart_failure'
    FIELD_BPHH_AFIB = 'atrial_fibrillation'
    FIELD_BPHH_BRCA = 'breast_cancer'
    FIELD_BPHH_OVCA = 'ovarian_cancer'
    FIELD_BPHH_PRCA = 'prostate_cancer'
    FIELD_BPHH_PACA = 'pancreatic_cancer'
    FIELD_BPHH_COCA = 'colorectal_cancer'
    FIELDS_BPHH_CURRENT = [
        FIELD_BPHH_HYPERTENSION,
        FIELD_BPHH_HYPERLIPID,
        FIELD_BPHH_T1DM,
        FIELD_BPHH_T2DM,
        FIELD_BPHH_KD,
        FIELD_BPHH_ASTHMA,
        FIELD_BPHH_OBESITY,
        FIELD_BPHH_SLEEPAPNEA,
        FIELD_BPHH_CHD,
        FIELD_BPHH_HF,
        FIELD_BPHH_AFIB,
        FIELD_BPHH_BRCA,
        FIELD_BPHH_OVCA,
        FIELD_BPHH_PRCA,
        FIELD_BPHH_PACA,
        FIELD_BPHH_COCA
    ]
    FIELDS_BPHH_PAST = [f'{x}_2' for x in FIELDS_BPHH_CURRENT]
    FIELDS_BPHH_RISK = [f'{x}_3' for x in FIELDS_BPHH_CURRENT]
    FIELDS_BPHH = FIELDS_BPHH_CURRENT + FIELDS_BPHH_PAST + FIELDS_BPHH_RISK

    # MeTree
    FIELD_METREE_JSON = 'metree_json'

    class YesNo(Enum):
        NO = '0'
        YES  = '1'

    class OrderStatus(Enum):
        NOT_ORDERED = '1'
        SUBMITTED = '2'
        RECEIVED = '3'
        COMPLETED = '4'

    class FormComplete(Enum):
        INCOMPLETE = '0'
        UNVERIFIED = '1'
        COMPLETE = '2'

    def __init__(self, endpoint, api_token):
        self.endpoint = endpoint
        self.api_token = api_token

        # PyCap expects endpoint to end with '/'
        if self.endpoint[-1] != '/':
            self.endpoint += '/'
        self.project = Project(self.endpoint, self.api_token)

        # Templates for order ID
        self._order_id_prefix = f'COLUMBIA_ORDER_{date.today().strftime("%Y%m%d")}_'
        self._order_id_template = self._order_id_prefix + '{:03d}'
        self._order_id_regex = self._order_id_prefix + '(\d{3})'
        # For keeping track of order numbers
        self._next_order_num = self._get_max_order_num()

    def pull_info_for_new_order(self):
        '''
        Eligible: (1) ready for order button checked; (2) Invitae order status is 0
        (1) Use a toggle flag in local redcap interface to show who is ready for putting a new order.
        Recruiters should check that box once the individual's sample being collected.
        (2) this will be updated automatically once the order is put successfully via redox.

        Return
        ------
        Dict of participant information required for Invitae order
        '''
        # Specify which forms and fields are needed from the record export
        # Get all fields from Invitae Ordering instrument and record_id and participant_lab_id
        forms = [Redcap._FORM_INVITAE_ORDER]
        fields_info = [Redcap.FIELD_RECORD_ID, Redcap.FIELD_LAB_ID,
                       Redcap.FIELD_NAME_FIRST, Redcap.FIELD_NAME_LAST,
                       Redcap.FIELD_DOB, Redcap.FIELD_SEX, Redcap.FIELD_RACE] + \
                       Redcap.FIELDS_BPHH_CURRENT + Redcap.FIELDS_BPHH_PAST
        fields_requirements = [Redcap.FIELD_AGE, Redcap.FIELD_SAMPLE_RECEIVED, Redcap.FIELD_SAMPLE_REPLACE,
                              Redcap.FIELD_ORDER_READY]
        fields = fields_info + fields_requirements

        participant_info = []
        records = self.project.export_records(fields=fields, forms=forms)
        for record in records:
            if record[Redcap.FIELD_ORDER_READY] == Redcap.YesNo.YES.value:
                # Perform various other safeguard checks before placing the order
                if (record[Redcap.FIELD_ORDER_STATUS] != Redcap.OrderStatus.NOT_ORDERED.value
                        and record[Redcap.FIELD_ORDER_STATUS]):
                    logger.warning(f'CUIMC ID {record[Redcap.FIELD_RECORD_ID]} was marked for submitting order, '
                                   'but the order status must be "Not ordered yet".')
                    continue
                elif record[Redcap.FIELD_SAMPLE_RECEIVED] != Redcap.YesNo.YES.value:
                    logger.warning(f'CUIMC ID {record[Redcap.FIELD_RECORD_ID]} was marked for submitting order, '
                                   'but the sample has not been received.')
                    continue
                elif record[Redcap.FIELD_SAMPLE_REPLACE] == Redcap.YesNo.YES.value:
                    logger.warning(f'CUIMC ID {record[Redcap.FIELD_RECORD_ID]} was marked for submitting order, '
                                   'but the sample needs to be replaced.')
                    continue
                elif int(record[Redcap.FIELD_AGE]) < 18:
                    logger.warning(f'CUIMC ID {record[Redcap.FIELD_RECORD_ID]} was marked for submitting order, '
                                   'but the participant age was under 18.')
                    continue
                else:
                    # Add participant to list of participants for ordering
                    participant_info.append({f:record[f] for f in fields_info})

        return participant_info

    def pull_info_for_query_order(self):
        '''
        Retrieves info of all participants whose order status should be queried:
        participants whose order has been submitted but has not yet been completed.

        Return
        ------
        Dict of participant information required for Invitae order query
        '''
        # Specify which forms and fields are needed from the record export
        # Get all fields from Invitae Ordering instrument and record_id and participant_lab_id
        forms = [Redcap._FORM_INVITAE_ORDER]
        fields = [Redcap.FIELD_RECORD_ID, Redcap.FIELD_LAB_ID,
                  Redcap.FIELD_NAME_FIRST, Redcap.FIELD_NAME_LAST,
                  Redcap.FIELD_DOB, Redcap.FIELD_SEX,
                  Redcap.FIELD_ORDER_STATUS]

        participant_info = []
        records = self.project.export_records(fields=fields, forms=forms)
        for record in records:
            if Redcap.OrderStatus.NOT_ORDERED.value < record[Redcap.FIELD_ORDER_STATUS] < Redcap.OrderStatus.COMPLETED.value:
                # Convert REDCap's sex values to the Redox value set
                record[Redcap.FIELD_SEX] = Redcap.map_redcap_sex_to_redox_sex(record[Redcap.FIELD_SEX])
                participant_info.append({f:record[f] for f in fields})

        # For testing, return the entire records
        return participant_info

    def get_new_order_id(self):
        '''
        Retrieves a new order ID for placing new Invitae orders.

        Return
        ------
        A new order ID
        '''
        if self._next_order_num is None:
            self._next_order_num = self._get_max_order_num()

        self._next_order_num += 1
        next_order_id = self._order_id_template.format(self._next_order_num)
        logger.debug(f'get_new_order_id: {next_order_id}')

        return next_order_id

    def _get_max_order_num(self):
        '''
        Gets the max order number in REDCap matching the current template
        '''
        records = self.project.export_records(fields=[Redcap.FIELD_ORDER_ID])

        max_order_id_num = 0
        if records:
            r = re.compile(self._order_id_regex)
            for rec in records:
                order_id = rec[Redcap.FIELD_ORDER_ID]
                try:
                    m = r.match(order_id)
                    if m:
                        order_id_num = int(m[1])
                        max_order_id_num = max(max_order_id_num, order_id_num)
                except ValueError:
                    continue

        return max_order_id_num

    def update_order_status(self, record_id, order_new=None, order_status=None, order_date=None, order_id=None):
        '''
        Update the Invitae order status in local redcap

        Params
        ------
        record_id: local REDCap record_id
        order_new: [Optional] REDCap.YesNo
        order_status: [Optional] REDCap.OrderStatus
        order_date: [Optional] date order placed in 'YYYY-MM-DD' format
        order_id: [Optional] locally created order ID

        Return
        ------
        True if successful
        '''
        # Build the updated record using only the supplied values
        record = {
            Redcap.FIELD_RECORD_ID: record_id
        }
        if order_new is not None:
            record[Redcap.FIELD_ORDER_READY] = order_new.value
        if order_status is not None:
            record[Redcap.FIELD_ORDER_STATUS] = order_status.value
        if order_date is not None:
            record[Redcap.FIELD_ORDER_DATE] = order_date
        if order_id is not None:
            record[Redcap.FIELD_ORDER_ID] = order_id

        if len(record) > 1:
            response = self.project.import_records([record])
            if response.get('count') == 1:
                logger.info('Successfully updated local REDCap with order status')
                return True
            else:
                logger.error(f'Unuccessful attempt to update local REDCap with order status: {record}. Response from update attempt: {response}')

        return True
