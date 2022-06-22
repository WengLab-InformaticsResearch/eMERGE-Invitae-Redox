from configparser import ConfigParser
import requests
import json


def read_api_config(config_file):
    api_token_file = config_file
    with open(api_token_file,'r') as f:
        api_conf = json.load(f)

    api_key_local = api_conf['api_key_local'] # API token for local
    api_key_r4 = api_conf['api_key_r4'] # API token for R4.
    cu_local_endpoint = api_conf['local_endpoint'] # local api endpoint
    r4_api_endpoint = api_conf['r4_api_endpoint'] # R4 api endpoint
    return api_key_local, api_key_r4, cu_local_endpoint, r4_api_endpoint

def get_record_list():
    '''
    return a list of record for cde extraction and r4 push
    '''

def extract_cde(record_id = "20"):
    '''
    hard coded for testing purpose. 
    '''
    gira_data = {}
    gira_data["record_id"] = record_id
    gira_data["count_positive_allergy"] = 3
    gira_data["allergy_test_flag"] = 1
    gira_data["hdl_lab_name"] = "HDL",
    gira_data["hdl_date_at_event"] = "2020-01-01"
    gira_data["hdl_measurement_concept_id"] = "3023602",
    gira_data["hdl_value_most_recent"] = "1"
    gira_data["totalcholest_lab_name"] = "total cholesterol"
    gira_data["totalcholest_date_at_event"] = "2020-12-01"
    gira_data["totalcholest_measurement_concept_id"] = "2212267"
    gira_data["totalcholest_value_most_recent"] = "185"
    gira_data["triglyceride_lab_name"] = "Triglyceride"
    gira_data["triglyceride_date_at_event"] = "2020-02-01" 
    gira_data["triglyceride_measurement_concept_id"] = "42868692"
    gira_data["triglyceride_value_most_recent"] = "100"
    gira_data["a1c_lab_name"] = "A1C"
    gira_data["a1c_date_at_event"] = "2020-03-01"
    gira_data["a1c_measurement_concept_id"] = "3004410"
    gira_data["a1c_value_most_recent"] = "5.5"
    gira_data["dbp_lab_name"] = "DBP"
    gira_data["dbp_date_at_event"] = "2020-03-01"
    gira_data["dbp_measurement_concept_id"] = "3012888"
    gira_data["dbp_value_most_recent"] = "80"
    gira_data["sbp_lab_name"] = "SBP"
    gira_data["sbp_date_at_event"] = "2020-03-01"
    gira_data["sbp_measurement_concept_id"] = "3004249"
    gira_data["sbp_value_most_recent"] = "80"
    gira_data["age_at_first_wheeze_event"] = "5"
    gira_data["age_at_second_wheeze_event"] = ""
    gira_data["wheezing_flag"] = "1"
    gira_data["age_at_first_eczema_event"] = ""
    gira_data["age_at_second_eczema_event"] = ""
    gira_data["eczema_flag"] = "0"
    gira_data["gira_clinical_variables_complete"] = "1"
    return gira_data

def push_to_R4(api_key_r4, r4_api_endpoint, gira_data):
    data = {
        'token': api_key_r4,
        'content': 'record',
        'action': 'import',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'overwrite',
        'forceAutoNumber': 'false',
        'data': json.dumps([gira_data]),
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    r = requests.post(r4_api_endpoint,data=data)


if __name__ == "__main__":
    parser = ConfigParser()
    _ = parser.read('./gira.config')
    r4_api_endpoint = parser.get('test', 'R4_REDCAP_URL')
    api_key_r4 = parser.get('test', 'R4_REDCAP_API_KEY')
    id_list = get_record_list()
    if id_list is None:
        exit()
    for record_id in id_list:
        gira_data = extract_cde(record_id = record_id)
        push_to_R4(api_key_r4, r4_api_endpoint, gira_data)

    


