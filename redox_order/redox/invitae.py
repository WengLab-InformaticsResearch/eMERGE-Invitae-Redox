from urllib.parse import urljoin
import requests
import logging
from importlib import resources
from datetime import datetime

from .model.order_new import Model as OrderNew
from .model.order_query import Model as OrderQuery
from .model.order_queryresponse import Model as QueryResponse
from . import json_templates

SEND_REDOX = False

logger = logging.getLogger('redox_application')

class RedoxInvitaeAPI:
    ENDPOINT_AUTH = 'auth/authenticate'
    ENDPOINT_ENDPOINT = 'endpoint'

    def __init__(self, api_base_url, api_key, client_secret):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.client_secret = client_secret

    def authenticate(self):
        url = urljoin(self.api_base_url, RedoxInvitaeAPI.ENDPOINT_AUTH)
        query = {
            "apiKey": self.api_key,
            "secret": self.client_secret
        }
        response = requests.post(url, json=query)

        if response.status_code == 200:
            logger.debug('Redox authenticated')
            response_json = response.json()
            self.access_token = response_json['accessToken']
            return True
        else:
            logger.error(f'Failed to receive Redox access token. Response: {response.status_code} - {response.text}. ')
            return False

    def put_new_order(self, facility_code,
                      patient_id, patient_name_first, patient_name_last, patient_dob, patient_sex, 
                      patient_redox_race, patient_invitae_ancestry,
                      provider_npi, provider_name_first, provider_name_last, order_id, test=False):
        logger.info(f'New order: {patient_id}')

        template = resources.read_text(json_templates, 'new_order_template.json')
        order = OrderNew.parse_raw(template)
        datetime_iso = datetime.now().isoformat()

        # Fill in Meta
        order.Meta.EventDateTime = datetime_iso
        order.Meta.Test = test
        order.Meta.FacilityCode = facility_code        

        # Fill in Patient
        patient = order.Patient
        patient.Identifiers[0].ID = patient_id
        demogs = patient.Demographics
        demogs.FirstName = patient_name_first
        demogs.LastName = patient_name_last
        demogs.DOB = patient_dob
        demogs.Sex = patient_sex

        # Fill in Order
        order.Order.ID = order_id
        order.TransactionDateTime = datetime_iso

        # Fill in Provider
        provider = order.Order.Provider
        provider.NPI = provider_npi
        provider.ID = provider_npi
        provider.IDType = 'NPI'
        provider.FirstName = provider_name_first
        provider.LastName = provider_name_last

        # TODO: Fill in ClinicalInfo if needed

        # Send new order
        url = urljoin(self.api_base_url, RedoxInvitaeAPI.ENDPOINT_ENDPOINT)
        j = order.json(exclude_unset=True)
        logger.debug(j)

        if SEND_REDOX:
            response = requests.post(url,
                                    headers={
                                        'Content-Type': 'application/json',
                                        'Authorization': f'Bearer {self.access_token}'
                                    },
                                    data=j)

            if response.status_code == 200:
                response_json = response.json()
                if RedoxInvitaeAPI.check_response(response_json):
                    logger.error(f'New order unsuccessful for ID {patient_id}.')
                    return False
                else:
                    logger.info(f'New order successful for ID {patient_id}')
                    return True
            else:
                logger.error(f'New order unsuccessful for ID {patient_id}. Response: {response.status_code} - {response.text}')
                return False
        else:
            logger.debug('In development mode, order was not sent to Redox')
            # Pretend successfully sent order
            return True

    def query_order(self, patient_id):
        logger.info(f'Query order: {patient_id}')

        # TODO: determine what information is required for Order Query
        template = resources.read_text(json_templates, 'query_order_template.json')
        order = OrderQuery.parse_raw(template)
        order.Patients[0].Identifiers[0].ID = patient_id  # put order for new patients.

        # Send order query
        url = urljoin(self.api_base_url, RedoxInvitaeAPI.ENDPOINT_ENDPOINT)
        j = order.json(exclude_unset=True)
        logger.debug(j)
        if SEND_REDOX:
            response = requests.post(url,
                                    headers={
                                        'Content-Type': 'application/json',
                                        'Authorization': f'Bearer {self.access_token}'
                                    },
                                    data=j)

            # TODO: need to find out what's in the returned data
            if response.status_code == 200:
                response_json = response.json()
                if RedoxInvitaeAPI.check_response(response_json):
                    logger.error(f'Query order unsuccessful for ID {patient_id}.')
                    return None
                else:
                    logger.info(f'Query order successful for ID {patient_id}')
                    return response_json
            else:
                logger.error(f'Query order unsuccessful for ID {patient_id}. Response: {response.status_code} - {response.text}')
                return None
        else:
            logger.debug('In development mode, order query was not sent to Redox')
            # Pretend successfully queried order
            return dict()

    @staticmethod
    def check_response(response):
        if response and ('Meta' in response):
            if 'Errors' in response['Meta']:
                errors = response['Meta']['Errors']
                if len(errors) > 0:
                    logger.error(f'{len(errors)} response errors')
                    for i, err in enumerate(errors):
                        logger.error(f'{i}: {err}')
                        return(1)
                else:
                    logger.debug('No errors')
                    return(0)
            else:
                logger.debug('No errors')
                return(0)
