from ast import Del
from turtle import left
from pyrsistent import b
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

def add_cuimc_id(r4_record,local_data_df, cuimc_id_latest):
    record_id = r4_record['record_id'] 
    participant_lab_id = r4_record['participant_lab_id'].strip().lower()
    first_name = r4_record['first_name'].strip().lower()
    last_name= r4_record['last_name'].strip().lower()
    date_of_birth= r4_record['date_of_birth'].strip().lower()
    empty_name_flag = (first_name == '' or  last_name == '' or date_of_birth == '')
    if record_id in local_data_df['record_id'].drop_duplicates().tolist():
        cuimc_id = local_data_df[local_data_df['record_id']==record_id]['cuimc_id'].drop_duplicates().tolist()[0]
        r4_yn = None
    elif participant_lab_id != "" and participant_lab_id in local_data_df['participant_lab_id'].tolist():
        cuimc_id = local_data_df[local_data_df['participant_lab_id']==participant_lab_id]['cuimc_id'].drop_duplicates().tolist()[0]
        r4_yn = None
    elif not empty_name_flag:
        subset_df = local_data_df
        subset_df = subset_df[subset_df['first_name']==first_name]
        subset_df = subset_df[subset_df['last_name']==last_name]
        subset_df = subset_df[subset_df['date_of_birth']==date_of_birth]
        if subset_df.shape[0] > 0:
            cuimc_id = subset_df['cuimc_id'].drop_duplicates().tolist()[0]
            r4_yn = None
        else:
            cuimc_id = cuimc_id_latest + 1
            cuimc_id_latest = cuimc_id
            r4_yn = "1"
    else:
        cuimc_id = None
        r4_yn = None
    return cuimc_id, cuimc_id_latest, r4_yn



def indexing_local_data(local_data):
    logging.info("indexing local dataset")
    local_data_df = pd.DataFrame(local_data)
    # identify the fields for mapping purpose in local data
    local_data_df = local_data_df[['cuimc_id','first_local','last_local','dob','participant_lab_id','record_id']]
    local_data_df = local_data_df.rename(columns={"first_local": "first_name", "last_local": "last_name", "dob": "date_of_birth"})
    # get latest CUIMC id
    cuimc_id_latest = local_data_df[['cuimc_id']].astype(int).max()[0]
    # clean up the fields on both for match purpose.
    local_data_df['first_name'] = local_data_df['first_name'].str.strip().str.lower()
    local_data_df['last_name'] = local_data_df['last_name'].str.strip().str.lower()
    local_data_df['date_of_birth'] = local_data_df['date_of_birth'].str.strip().str.lower()
    local_data_df['participant_lab_id'] = local_data_df['participant_lab_id'].str.strip().str.lower()
    return local_data_df, cuimc_id_latest

def push_data_to_local(api_key_local, cu_local_endpoint, r4_record):
    # check is it a redcap_repeat_instrument
    if r4_record['redcap_repeat_instance'] != '':
        del r4_record['record_id']
        del r4_record['r4_yn']
    else:
        if r4_record['r4_yn'] is None:
            del r4_record['r4_yn']

    data = {
        'token': api_key_local,
        'content': 'record',
        'action': 'import',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'overwrite',
        'forceAutoNumber': 'false',
        'data': json.dumps([r4_record]),
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    flag = 1
    while(flag > 0 and flag < 5):
        r = requests.post(cu_local_endpoint,data=data)
        if r.status_code == 200:
            logging.info('HTTP Status: ' + str(r.status_code))
            flag = 0
        else:
            logging.info('HTTP Status: ' + str(r.status_code) + '. R4 record_id: ' + r4_record['record_id'])
            flag = flag + 1

def update_local(api_key_local,cu_local_endpoint,local_data_df, r4_data, cuimc_id_latest):
    logging.info("update local redcap...")
    for r4_record in r4_data:
        cuimc_id, cuimc_id_latest, r4_yn = add_cuimc_id(r4_record,local_data_df, cuimc_id_latest)
        if cuimc_id is not None:
            r4_record['cuimc_id'] = str(cuimc_id)
            r4_record['r4_yn'] = r4_yn # new record indicator
            push_data_to_local(api_key_local,cu_local_endpoint,r4_record)
            
if __name__ == "__main__":
    api_key_local, api_key_r4, cu_local_endpoint, r4_api_endpoint = read_api_config()
    local_data = export_data_from_redcap(api_key_local,cu_local_endpoint)
    r4_data = export_data_from_redcap(api_key_r4,r4_api_endpoint)
    if r4_data != []:
        local_data_df, cuimc_id_latest = indexing_local_data(local_data)
        update_local(api_key_local,cu_local_endpoint,local_data_df, r4_data, cuimc_id_latest)
    
