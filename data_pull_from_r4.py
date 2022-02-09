import requests
import json
from pprint import pprint
from datetime import datetime
import pandas as pd
import datetime

today = datetime.date.today()
print(today)
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
flag = 1
while(flag):
    try:
        r = requests.post(cu_local_endpoint,data=data)
        meta_local_json = r.json()
        print('HTTP Status: ' + str(r.status_code))
        flag = 0
    except:
        print(r.json())



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


meta_json = meta_local_json + meta_r4_json

# export data from r4.
data = {
    'token': api_key_r4,
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}
r = requests.post(r4_api_endpoint,data=data)
print('HTTP Status: ' + str(r.status_code))
r4_data = r.json()
# export data (only used for match purpose) from local.
data['token'] = api_key_local
r = requests.post(cu_local_endpoint,data=data)
local_data = r.json()
# map between R4 and local redcap
local_data_df = pd.DataFrame(local_data)
r4_data_df = pd.DataFrame(r4_data)
# identify the mapping requirement
local_data_df = local_data_df[['cuimc_id','first_local','last_local','dob','participant_lab_id']]
local_data_df = local_data_df.rename(columns={"first_local": "first_name", "last_local": "last_name", "dob": "date_of_birth"})
# clean up the field for match purpose.
local_data_df['first_name'] = local_data_df['first_name'].str.strip().str.lower()
local_data_df['last_name'] = local_data_df['last_name'].str.strip().str.lower()
local_data_df['date_of_birth'] = local_data_df['date_of_birth'].str.strip().str.lower()
local_data_df['participant_lab_id'] = local_data_df['participant_lab_id'].str.strip().str.lower()
r4_data_df['first_name'] = r4_data_df['first_name'].str.strip().str.lower()
r4_data_df['last_name'] = r4_data_df['last_name'].str.strip().str.lower()
r4_data_df['date_of_birth'] = r4_data_df['date_of_birth'].str.strip().str.lower()
r4_data_df['participant_lab_id'] = r4_data_df['participant_lab_id'].str.strip().str.lower()
# if no participant lab IDs in local redcap
# match by names and DOB.
noid_local_df = local_data_df[local_data_df['participant_lab_id']=='']
noid_local_df.drop(['participant_lab_id'], axis=1,inplace=True) # to avoid duplicate conflict. 
# only match those with valid names and DOB
noid_local_df = noid_local_df[noid_local_df['first_name']!='']
noid_local_df = noid_local_df[noid_local_df['last_name']!='']
noid_local_df = noid_local_df[noid_local_df['date_of_birth']!=''] # may want to lose this in case there is DOB error?
# match r4 record_id.
noid_update_r4_df = noid_local_df.merge(r4_data_df,how='inner',on=['first_name','last_name','date_of_birth'])
noid_update_r4_df = noid_update_r4_df[['cuimc_id','record_id']].drop_duplicates()

# # if exist participant lab IDs in local redcap
# match by lab ID.
id_local_df = local_data_df[local_data_df['participant_lab_id']!='']
id_local_df.drop(['first_name'], axis=1,inplace=True) # to avoid duplicate conflict. 
id_local_df.drop(['last_name'], axis=1,inplace=True) # to avoid duplicate conflict. 
id_local_df.drop(['date_of_birth'], axis=1,inplace=True) # to avoid duplicate conflict. 
# only match those with valid lab id.
# id_local_df = id_local_df[id_local_df['participant_lab_id']!='']
# match r4 record_id
id_update_r4_df = id_local_df.merge(r4_data_df,how='inner',on=['participant_lab_id'])
id_update_r4_df = id_update_r4_df[['cuimc_id','record_id']].drop_duplicates()

# build id mapping df for r4 data extraction.
record_id_update_df = pd.concat([id_update_r4_df,noid_update_r4_df]).drop_duplicates()

# extract R4
r4_merge_df = r4_data_df.merge(record_id_update_df)
r4_merge_df.drop(['record_id'], axis=1,inplace=True) # to avoid duplicate conflict. 

# sync to local redcap
result = json.loads(r4_merge_df.to_json(orient="records"))
for record in result:
    data = {
        'token': api_key_local,
        'content': 'record',
        'action': 'import',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'overwrite',
        'forceAutoNumber': 'false',
        'data': json.dumps([record]),
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    flag = 1
    while(flag):
        try:
            r = requests.post(cu_local_endpoint,data=data)
            print('HTTP Status: ' + str(r.status_code))
            print(r.text)
            flag = 0
        except:
            print(r.json())