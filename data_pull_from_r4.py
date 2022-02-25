from turtle import left
import requests
import json
from datetime import datetime
import pandas as pd
import logging

logging.basicConfig(filename='./data-pull.log', level=logging.INFO)
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
logging.info("Current Time =" +  dt_string)


def read_api_config(config_file = './api_tokens.json'):
    logging.info("reading api tokens and endpoint url...")
    api_token_file = config_file
    with open(api_token_file,'r') as f:
        api_conf = json.load(f)

    api_key_local = api_conf['api_key_local'] # API token for local
    api_key_r4 = api_conf['api_key_r4'] # API token for R4.
    cu_local_endpoint = api_conf['local_endpoint'] # local api endpoint
    r4_api_endpoint = api_conf['r4_api_endpoint'] # R4 api endpoint
    return api_key_local, api_key_r4, cu_local_endpoint, r4_api_endpoint

def export_data_from_redcap(api_key, api_endpoint):
    logging.info("export data from " + api_endpoint)
    data = {
        'token': api_key,
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
    flag = 1
    while(flag > 0 and flag < 5):
        r = requests.post(api_endpoint,data=data)
        logging.info('HTTP Status: ' + str(r.status_code))
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            flag = flag + 1
       

def merge_data(local_data, r4_data):
    logging.info("merging two datasets")
    local_data_df = pd.DataFrame(local_data)
    r4_data_df = pd.DataFrame(r4_data)

    # identify the fields for mapping purpose in local data
    local_data_df = local_data_df[['cuimc_id','first_local','last_local','dob','participant_lab_id']]
    local_data_df = local_data_df.rename(columns={"first_local": "first_name", "last_local": "last_name", "dob": "date_of_birth"})

    # get latest CUIMC id
    cuimc_id_latest = local_data_df[['cuimc_id']].astype(int).max()[0]

    # clean up the fields on both for match purpose.
    local_data_df['first_name'] = local_data_df['first_name'].str.strip().str.lower()
    local_data_df['last_name'] = local_data_df['last_name'].str.strip().str.lower()
    local_data_df['date_of_birth'] = local_data_df['date_of_birth'].str.strip().str.lower()
    local_data_df['participant_lab_id'] = local_data_df['participant_lab_id'].str.strip().str.lower()
    r4_data_df['first_name'] = r4_data_df['first_name'].str.strip().str.lower()
    r4_data_df['last_name'] = r4_data_df['last_name'].str.strip().str.lower()
    r4_data_df['date_of_birth'] = r4_data_df['date_of_birth'].str.strip().str.lower()
    r4_data_df['participant_lab_id'] = r4_data_df['participant_lab_id'].str.strip().str.lower()

    # if no participant lab IDs in local data, then matched by names and DOB.
    noid_local_df = local_data_df[local_data_df['participant_lab_id']=='']
    noid_local_df.drop(['participant_lab_id'], axis=1,inplace=True) # to avoid duplicate conflict. 
    # only match those with valid names and DOB
    noid_local_df = noid_local_df[noid_local_df['first_name']!='']
    noid_local_df = noid_local_df[noid_local_df['last_name']!='']
    noid_local_df = noid_local_df[noid_local_df['date_of_birth']!=''] # may want to lose this in case there is DOB error?
    # match r4 record_id.
    noid_update_r4_df = noid_local_df.merge(r4_data_df,how='inner',on=['first_name','last_name','date_of_birth'])
    noid_update_r4_df = noid_update_r4_df[['cuimc_id','record_id']].drop_duplicates()

    # if exist participant lab IDs in local redcap, then matched by lab ID.
    id_local_df = local_data_df[local_data_df['participant_lab_id']!='']
    id_local_df.drop(['first_name'], axis=1,inplace=True) # to avoid duplicate conflict. 
    id_local_df.drop(['last_name'], axis=1,inplace=True) # to avoid duplicate conflict. 
    id_local_df.drop(['date_of_birth'], axis=1,inplace=True) # to avoid duplicate conflict. 
    # match r4 record_id
    id_update_r4_df = id_local_df.merge(r4_data_df,how='inner',on=['participant_lab_id'])
    id_update_r4_df = id_update_r4_df[['cuimc_id','record_id']].drop_duplicates()

    # build id mapping df for r4 data extraction.
    record_id_update_df = pd.concat([id_update_r4_df,noid_update_r4_df]).drop_duplicates()

    # left merge: if matched with local, update, otherwise add new records by assigning a auto incremented cuimc_id
    r4_merge_df = r4_data_df.merge(record_id_update_df,how='left')
    r4_merge_df.drop(['record_id'], axis=1,inplace=True) # to avoid duplicate conflict. 

    # convert to json.
    merged_records = json.loads(r4_merge_df.to_json(orient="records"))

    return merged_records, cuimc_id_latest

def update_local(merged_records,api_key_local,cu_local_endpoint,cuimc_id_latest): 
    logging.info("update local redcap...")
    for record in merged_records:
        if record['cuimc_id'] is None:
            # assign new id auto incremented.
            record['cuimc_id'] = str(cuimc_id_latest + 1)
            record['r4_yn'] = "1" # new record indicator
            cuimc_id_latest = cuimc_id_latest + 1
        
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
        while(flag > 0 and flag < 5):
            r = requests.post(cu_local_endpoint,data=data)
            logging.info('HTTP Status: ' + str(r.status_code))
            if r.status_code == 200:
                flag = 0
            else:
                flag = flag + 1

if __name__ == "__main__":
    api_key_local, api_key_r4, cu_local_endpoint, r4_api_endpoint = read_api_config()
    local_data = export_data_from_redcap(api_key_local,cu_local_endpoint)
    r4_data = export_data_from_redcap(api_key_r4,r4_api_endpoint)
    if r4_data != []:
        merged_records, cuimc_id_latest = merge_data(local_data, r4_data)
        update_local(merged_records,api_key_local,cu_local_endpoint,cuimc_id_latest)
    
