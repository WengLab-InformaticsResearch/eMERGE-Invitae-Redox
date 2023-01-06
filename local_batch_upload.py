from distutils.command.config import config
from distutils.command.upload import upload
import requests
import json
from datetime import datetime
import pandas as pd
import numpy as np
import logging
import argparse

def read_api_config(config_file):
    logging.info("reading api tokens and endpoint url...")
    api_token_file = config_file
    with open(api_token_file,'r') as f:
        api_conf = json.load(f)

    api_key_local = api_conf['api_key_local'] # API token for local
    api_key_r4 = api_conf['api_key_r4'] # API token for R4.
    cu_local_endpoint = api_conf['local_endpoint'] # local api endpoint
    r4_api_endpoint = api_conf['r4_api_endpoint'] # R4 api endpoint
    return api_key_local, api_key_r4, cu_local_endpoint, r4_api_endpoint

def read_batch_upload_csv(csv_file):
    df = pd.read_csv(csv_file,dtype=object)
    df['dob'] = pd.to_datetime(df['dob'])
    df['dob_child'] = pd.to_datetime(df['dob_child'])
    df = df.fillna('')
    return df

def clean_upload(upload_df, existing_df, replicate_records_csv):
    '''
    There are three reasons a record won't be uploaded.
    1. empty mrn
    2. empty names and dob
    3. existing record matched by mrn or name + dob
    '''
    upload_init_df = upload_df.copy(deep=True)
    # clean empty mrn
    upload_df = upload_df[upload_df['mrn']!='']
    # clean empty names and dobs
    upload_df = upload_df[upload_df['last_local']!='']
    upload_df = upload_df[upload_df['first_local']!='']
    upload_df = upload_df[upload_df['dob']!='']

    existing_mrns = existing_df['mrn'].drop_duplicates().to_list()
    existing_mrns = [i for i in existing_mrns if i!='']
    # replicated_df1 = upload_df[upload_df['mrn'].isin(existing_mrns)]
    upload_df = upload_df[~upload_df['mrn'].isin(existing_mrns)]
    name_local_df = existing_df[['last_local','first_local','dob','last_child','child_first','dob_child']]
    name_local_df = name_local_df.apply(lambda x: x.astype(str).str.lower().str.strip())
    name_r4_df = existing_df[['last_name','first_name','date_of_birth','last_name_child','first_name_child','date_of_birth_child']]
    name_r4_df = name_r4_df.apply(lambda x: x.astype(str).str.strip().str.lower())
    name_r4_df = name_r4_df.rename(columns={"last_name": "last_local", "first_name": "first_local", "date_of_birth": "dob","last_name_child":"last_child","first_name_child":"child_first","date_of_birth_child":"dob_child"})
    existing_name = pd.concat([name_local_df,name_r4_df]).drop_duplicates(keep="first")
    upload_df = upload_df.copy(deep=True).apply(lambda x: x.astype(str).str.strip().str.lower())
    upload_df = pd.merge(upload_df,existing_name,on=['last_local','first_local','dob','last_child','child_first','dob_child'],how="outer",indicator=True)
    # replicated_df2 = upload_df[upload_df['_merge']=='both']
    # replicated_df2 = replicated_df2.drop(columns='_merge')
    upload_df = upload_df[upload_df['_merge']=='left_only']
    upload_df = upload_df.drop(columns='_merge')
    # patch 2022-10-18, fix date format
    upload_df['dob'] = pd.to_datetime(upload_df['dob'].astype(str)).dt.strftime('%m/%d/%Y')
    upload_df['dob_child'] = pd.to_datetime(upload_df['dob_child'].astype(str)).dt.strftime('%m/%d/%Y')
    upload_df = upload_df.fillna('')
    cleaned_results = upload_init_df[~upload_init_df['cuimc_id'].isin(upload_df['cuimc_id'].to_list())]
    cleaned_results.to_csv(replicate_records_csv,index=None)
    return upload_df

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def get_local_record(api_key_local,cu_local_endpoint):
    data = {
        'token': api_key_local,
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
        r = requests.post(cu_local_endpoint,data=data)
        if r.status_code == 200:
            logging.info('HTTP Status: ' + str(r.status_code))
            data = r.json()
            flag = 0
        else:
            logging.error('Error occured in exporting data from ' + cu_local_endpoint)
            logging.error('HTTP Status: ' + str(r.status_code))
            logging.error(r.content)
            flag = flag + 1
    df = pd.DataFrame(data)
    return df

def get_lastest_cuimd_id(api_key_local,cu_local_endpoint, local_df):
    local_df['cuimc_id'] = local_df['cuimc_id'].astype(int)
    cuimc_id_latest = local_df[['cuimc_id']].max()[0]
    return cuimc_id_latest

def prepare_batch_upload(api_key_local, cu_local_endpoint, upload_df,local_df,replicate_records_csv):
    cuimc_id_latest = get_lastest_cuimd_id(api_key_local,cu_local_endpoint,local_df) + 1
    upload_df_cleaned = clean_upload(upload_df,local_df,replicate_records_csv)
    batch_records = upload_df_cleaned.to_dict('records')

    for record in batch_records:
        record['cuimc_id'] = str(cuimc_id_latest)
        record['local_batch_upload'] = "1"
        cuimc_id_latest = cuimc_id_latest + 1
    
    upload_data = json.dumps(batch_records, cls=NpEncoder)
    data = {
        'token': api_key_local,
        'content': 'record',
        'action': 'import',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'normal', # to avoid some edge cases
        'forceAutoNumber': 'false',
        'data': upload_data,
        'returnContent': 'count',
        'dateFormat': 'MDY',
        'returnFormat': 'json'
    }
    return data

def execute_batch_upload(data, cu_local_endpoint, flag = 1, max_try = 5):
    while(flag > 0 and flag < max_try):
        r = requests.post(cu_local_endpoint,data=data)
        if r.status_code == 200:
            logging.info('HTTP Status: ' + str(r.status_code))
            flag = 0
        else:
            logging.error('Error occured in importing data to ' + cu_local_endpoint)
            logging.error(r.content)
            flag = flag + 1


if __name__ == "__main__":
    log_file = '/phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/batch_upload.log'
    token_file = '/phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/api_tokens.json'
    csv_file = '/phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/batch_upload_to_local_redcap/drlantigua_drsinger_drevans_upload_local_10-31-22.csv'
    replicate_records_csv_file = '/phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/batch_upload_to_local_redcap/drlantigua_drsinger_drevans_upload_local_10-31-22_failed.csv'
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--log', type=str, required=True, help="file to write log",)    
    # parser.add_argument('--token', type=str, required=True, help='json file with api tokens')    
    # args = parser.parse_args()
    # log_file = args.log
    # token_file = args.token
    

    logging.basicConfig(filename=log_file, level=logging.INFO)
    # logging.basicConfig(level=logging.INFO)
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logging.info("Current Time =" +  dt_string)

    api_key_local, _, cu_local_endpoint, _ = read_api_config(config_file = token_file)
    upload_df = read_batch_upload_csv(csv_file)
    local_df = get_local_record(api_key_local,cu_local_endpoint)
    upload_data = prepare_batch_upload(api_key_local,cu_local_endpoint,upload_df,local_df,replicate_records_csv_file)
    execute_batch_upload(upload_data,cu_local_endpoint)    
