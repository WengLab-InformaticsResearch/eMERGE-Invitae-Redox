import requests
import json


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

# new_json = []
# form_name_current = ""
# for meta_local_field in meta_local_json:
#     form_name_new = meta_local_field['form_name']
#     if (form_name_new == form_name_current) or form_name_current == "":
#         new_json.append(meta_local_field)
#         form_name_current = form_name_new
#     else:
#         for meta_r4_field in meta_r4_json_deduplicated:
#             if meta_r4_field['form_name'] == form_name_current:
#                 new_json.append(meta_r4_field)
#         form_name_current = form_name_new

meta_json = meta_local_json + meta_r4_json_deduplicated
# redcap requires form in sequential order.
# meta_json.sort(key=lambda x: x["form_name"]) # this will change the order and re-assign the record id.
ordered_form_names = []
for i in meta_json:
    if i['form_name'] not in ordered_form_names:
        ordered_form_names.append(i['form_name'])
new_json = []
for i in ordered_form_names:
    for j in meta_json:
        if j['form_name'] == i:
            new_json.append(j)

with open('./test_meta.json','w') as f:
    json.dump(new_json,f)

# update local data dictionary
# IMPORTANT: need to re-arrange the 
data = {
    'token': api_key_local,
    'content': 'metadata',
    'format': 'json',
    'returnFormat': 'json',
    'data': json.dumps(new_json)
}
r = requests.post(cu_local_endpoint,data=data)
print('HTTP Status: ' + str(r.status_code))
print('HTTP Status: ' + r.content.decode('utf-8'))

