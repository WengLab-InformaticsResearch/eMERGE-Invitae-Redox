from urllib.parse import urljoin
import requests
import json
import logging

logger = logging.getLogger('redox_application')

class Redcap:
    def __init__(self, endpoint, api_token):
        self.endpoint = endpoint
        self.api_token = api_token

    def pull_batch_ids(self):
        '''
        Eligible: (1) ready for order button checked; (2) Invitae order status is 0
        (1) Use a toggle flag in local redcap interface to show who is ready for putting a new order.
        Recruiters should check that box once the individual's sample being collected.
        (2) this will be updated automatically once the order is put successfully via redox.
        return participant_id
        '''
        return ['fakeID0001', 'fakeID0002']

    def update_order_status(self, participant_id):
        '''
        Update the Invitae order status in local redcap if an order is put successfully.
        '''
        return True