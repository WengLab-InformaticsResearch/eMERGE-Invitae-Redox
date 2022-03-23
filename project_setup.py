import requests
import json
from pprint import pprint
from datetime import datetime
import pandas as pd
from io import StringIO


api_token_file = './api_tokens.json'
with open(api_token_file,'r') as f:
    api_conf = json.load(f)

api_key_local = api_conf['api_key_local'] # API token for local
api_key_r4 = api_conf['api_key_r4'] # API token for R4.
cu_local_endpoint = api_conf['local_endpoint'] # local api endpoint
r4_api_endpoint = api_conf['r4_api_endpoint'] # R4 api endpoint

# local Data dictionary export
data = {
    'token': api_key_local,
    'content': 'metadata',
    'format': 'json',
    'returnFormat': 'json'
}
r = requests.post(cu_local_endpoint,data=data)
meta_local_json = r.json()
print('HTTP Status: ' + str(r.status_code))

# R4 Data dictionary export
data = {
    'token': api_key_r4,
    'content': 'metadata',
    'format': 'json',
    'returnFormat': 'json'
}
r = requests.post(r4_api_endpoint,data=data)
meta_r4_json = r.json()
print('HTTP Status: ' + str(r.status_code))

# remove field already existing.
meta_local_json_field_name_list = [i['field_name'] for i in meta_local_json]
meta_r4_json_deduplicated = [i for i in meta_r4_json if i['field_name'] not in meta_local_json_field_name_list]
meta_json = meta_local_json + meta_r4_json_deduplicated
# redcap requires form in sequential order.
meta_json.sort(key=lambda x: x["form_name"])
# update local data dictionary
data = {
    'token': api_key_local,
    'content': 'metadata',
    'format': 'json',
    'returnFormat': 'json',
    'data': json.dumps(meta_json)
}
r = requests.post(cu_local_endpoint,data=data)
print('HTTP Status: ' + str(r.status_code))
print('HTTP Status: ' + r.content.decode('utf-8'))

