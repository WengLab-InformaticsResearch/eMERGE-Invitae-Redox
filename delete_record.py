import requests
import json

def read_api_config(config_file = './api_tokens.json'):
    api_token_file = config_file
    with open(api_token_file,'r') as f:
        api_conf = json.load(f)

    api_key_local = api_conf['api_key_local'] # API token for local
    api_key_r4 = api_conf['api_key_r4'] # API token for R4.
    cu_local_endpoint = api_conf['local_endpoint'] # local api endpoint
    r4_api_endpoint = api_conf['r4_api_endpoint'] # R4 api endpoint
    return api_key_local, api_key_r4, cu_local_endpoint, r4_api_endpoint

def delete_record(record_id,api_key_local,cu_local_endpoint):
    data = {
        'token': api_key_local,
        'action': 'delete',
        'content': 'record',
        'records[0]': str(record_id),
    }
    r = requests.post(cu_local_endpoint,data=data)
    print('HTTP Status: ' + str(r.status_code))
    print(r.text)

if __name__ == "__main__":
    api_key_local, api_key_r4, cu_local_endpoint, r4_api_endpoint = read_api_config()
    record_id_list = [24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52]
    for record_id in record_id_list:
        delete_record(record_id,api_key_local,cu_local_endpoint)