from ast import Del
from configparser import ConfigParser
from urllib.parse import urljoin
import requests
import json


def get_redox_access_token(api_base_url, api_key, client_secret):
    url = urljoin(api_base_url, 'auth/authenticate')
    query = {"apiKey": f"{api_key}", "secret": f"{client_secret}"}
    response = requests.post(url, json=query)
    if response.status_code == 200:
        return response.json()
    else:
        return None
def pull_batch_ids(redcap_api_token,redcap_api_endpoint):
    '''
    Eligible: (1) ready for order button checked; (2) Invitae order status is 0
    (1) Use a toggle flag in local redcap interface to show who is ready for putting a new order.
    Recruiters should check that box once the individual's sample being collected.
    (2) this will be updated automatically once the order is put successfully via redox.
    return participant_id
    '''

def update_order_status(redcap_api_token,redcap_api_endpoint, participant_id):
    '''
    Update the Invitae order status in local redcap if an order is put successfully. 
    '''


def put_new_order(api_base_url, token, patient_id = "0000000002"):
    url = urljoin(api_base_url, 'endpoint')
    minimum_payroll = json.load(open('./new_order_template.json'))
    minimum_payroll['Patient']['Identifiers'][0]['ID'] = patient_id # put order for new patients.
    response = requests.post(url, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, json=minimum_payroll)
    return response.json()

def query_order(api_base_url, token, patient_id = "0000000002"):
    url = urljoin(api_base_url, 'endpoint')
    minimum_payroll = json.load(open('./query_order_template.json'))
    minimum_payroll['Patient']['Identifiers'][0]['ID'] = patient_id # put order for new patients.
    response = requests.post(url, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, json=minimum_payroll)
    return response.json()

def check_response(response):
    if response and ('Meta' in response):
        if 'Errors' in response['Meta']:
            errors = response['Meta']['Errors']
            if len(errors) > 0:
                for err in errors:
                    print(err)
                    return(1)
            else:
                print('No errors')
                return(0)         
        else:
            print('No errors')
            return(0)

if __name__ == "__main__":

    

    parser = ConfigParser()
    _ = parser.read('./redox-api.config')
    api_base_url = parser.get('test', 'BASE_URL')
    redcap_api_endpoint = parser.get('test', 'LOCAL_REDCAP_URL')
    redcap_api_token = parser.get('test', 'LOCAL_REDCAP_API_KEY')
    token_response = get_redox_access_token(api_base_url, parser.get('test', 'KEY'), parser.get('test', 'CLIENT_SECRET'))
    #token_response  # If you want to see what it looks like


    id_for_ordering = pull_batch_ids(redcap_api_endpoint=redcap_api_endpoint,redcap_api_token=redcap_api_token)
    if id_for_ordering is None:
        exit()
    for participant_id in id_for_ordering:
        response = put_new_order(api_base_url, token_response['accessToken'], patient_id = participant_id)
        if check_response(response):
            next
        response = query_order(api_base_url, token_response['accessToken'], patient_id = participant_id)
        if check_response(response):
            next
        update_order_status(redcap_api_endpoint=redcap_api_endpoint,redcap_api_token=redcap_api_token, participant_id = participant_id)


