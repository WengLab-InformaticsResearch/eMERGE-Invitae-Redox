import requests
import json


# read configs.
api_token_file = './test_api_tokens.json'
with open(api_token_file,'r') as f:
    api_conf = json.load(f)

api_key_local = api_conf['api_key_local'] # API token for local
api_key_r4 = api_conf['api_key_r4'] # API token for R4.
cu_local_endpoint = api_conf['local_endpoint'] # local api endpoint
r4_api_endpoint = api_conf['r4_api_endpoint'] # R4 api endpoint


# input parameters.
mrn = 1000000000
cuimc_id = ''
r4_record_id = ''
# option first_name, last_name, dob.
ehr_first_name = 'abc'
ehr_last_name = 'efg'
ehr_dob = '2000-01-01'
file_field = 'completed_signed_consent' # can be replaced later using gira report field
download_from_local = True

# find cuimc id by MRN
data = {
    'token': api_key_local,
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'fields[0]': 'mrn',
    'fields[1]': 'cuimc_id',
    'fields[2]': 'record_id',
    'fields[3]': 'participant_date_of_birth',
    'fields[4]': 'participant_first_name',
    'fields[5]': 'participant_last_name',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json',
    'filterLogic': '[mrn] = {mrn}'.format(mrn = mrn)
}
r = requests.post(cu_local_endpoint,data=data)
print('HTTP Status: ' + str(r.status_code))
print(r.json())
if r.status_code == 200:
    cuimc_id_list = r.json()
    if len(cuimc_id_list) == 1:
        # [optional]: double check names and dob
        flag = 1
        if r.json()[0]['participant_first_name'] != ehr_first_name: 
            flag = 0
        if r.json()[0]['participant_last_name'] != ehr_last_name: 
            flag = 0
        if r.json()[0]['participant_date_of_birth'] != ehr_dob:
            flag = 0
        if flag == 1:
            cuimc_id = r.json()[0]['cuimc_id']
            r4_record_id = r.json()[0]['record_id']


if download_from_local == True and cuimc_id != '': # download locally
    data = {
        'token': api_key_local,
        'content': 'file',
        'action': 'export',
        'record': cuimc_id,
        'field': file_field,
        'event': '',
        'returnFormat': 'json'
    }
    r = requests.post(cu_local_endpoint,data=data)
    print('HTTP Status: ' + str(r.status_code))
    file_path = './test_{cuimc_id}.{file_field}.pdf'.format(cuimc_id = cuimc_id, file_field = file_field)
    if r.status_code == 200:
        f = open(file_path, 'wb')
        f.write(r.content)
        f.close()
        print('GIRA report downloaded for {mrn}'.format(mrn = mrn))

elif download_from_local == False and r4_record_id != '': # download from r4
    data = {
        'token': api_key_r4,
        'content': 'file',
        'action': 'export',
        'record': r4_record_id,
        'field': file_field,
        'event': '',
        'returnFormat': 'json'
    }
    r = requests.post(r4_api_endpoint,data=data)
    print('HTTP Status: ' + str(r.status_code))
    file_path = './test_{cuimc_id}.{file_field}.pdf'.format(cuimc_id = cuimc_id, file_field = file_field)
    if r.status_code == 200:
        f = open(file_path, 'wb')
        f.write(r.content)
        f.close()
        print('GIRA report downloaded for {mrn}'.format(mrn = mrn))
else:  # not available
    print('No GIRA report available for {mrn}'.format(mrn = mrn))
 
    

