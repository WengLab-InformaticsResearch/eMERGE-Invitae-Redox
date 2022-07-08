from urllib.parse import urljoin
import json
import logging
from enum import Enum

import requests
from redcap import Project

logger = logging.getLogger('redox_application')

class Redcap:
    _FORM_INVITAE = 'invitae_ordering'

    # REDCap variable names
    # IDs
    FIELD_RECORD_ID = 'record_id'
    FIELD_LAB_ID = 'participant_lab_id'
    # Participant Info
    FIELD_DOB = 'date_of_birth'
    FIELD_NAME_FIRST = 'first_name'
    FIELD_NAME_MIDDLE = 'middle_name'
    FIELD_NAME_LAST = 'last_name'
    # Invitae Order
    FIELD_ORDER_READY = 'invitae_order_ready'
    FIELD_ORDER_ID = 'invitae_order_id'
    FIELD_ORDER_DATE = 'invitae_order_date'
    FIELD_ORDER_STATUS = 'invitae_order_status'
    FIELD_ORDER_FORM_COMPLETE = 'invitae_ordering_complete'


    class OrderReady(Enum):
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
        forms = [Redcap._FORM_INVITAE]
        fields = [Redcap.FIELD_RECORD_ID, Redcap.FIELD_LAB_ID,
                  Redcap.FIELD_NAME_FIRST, Redcap.FIELD_NAME_MIDDLE, Redcap.FIELD_NAME_LAST]

        participant_info = []
        records = self.project.export_records(fields=fields, forms=forms)
        for record in records:
            if record[Redcap.FIELD_ORDER_READY] == Redcap.OrderReady.YES.value and \
                    record[Redcap.FIELD_ORDER_FORM_COMPLETE] == Redcap.FormComplete.COMPLETE.value and \
                    (record[Redcap.FIELD_ORDER_STATUS] == Redcap.OrderStatus.NOT_ORDERED.value or
                        not record[Redcap.FIELD_ORDER_STATUS]):
                # TODO: check which variables required when the child is the participant
                participant_info.append({f:record[f] for f in fields})

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
        forms = [Redcap._FORM_INVITAE]
        fields = [Redcap.FIELD_RECORD_ID, Redcap.FIELD_LAB_ID,
                  Redcap.FIELD_NAME_FIRST, Redcap.FIELD_NAME_MIDDLE, Redcap.FIELD_NAME_LAST]

        participant_info = []
        records = self.project.export_records(fields=fields, forms=forms)
        for record in records:
            if Redcap.OrderStatus.NOT_ORDERED.value < record[Redcap.FIELD_ORDER_STATUS] < Redcap.OrderStatus.COMPLETED.value:
                # TODO: check which variables required when the child is the participant
                participant_info.append(record)

        # For testing, return the entire records
        return participant_info

    def update_order_status(self, record_id, order_status=None, order_date=None, order_id=None):
        '''
        Update the Invitae order status in local redcap

        Params
        ------
        record_id: local REDCap record_id
        order_status: [Optional] REDCap.OrderStatus
        order_date: [Optional] date order placed in 'YYYY-MM-DD' format
        order_id: [Optional] locally created order ID

        Return
        ------
        True if successful
        '''
        # Build the updated record using only the supplied values
        record = {
            'record_id': record_id
        }
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