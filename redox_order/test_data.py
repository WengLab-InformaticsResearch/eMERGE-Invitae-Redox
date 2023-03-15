import logging
import json
from configparser import ConfigParser

from redcap_invitae import Redcap

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('redox_testing.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

logger.info('Begin Invitae Redox test script')

# Read config file
parser = ConfigParser(inline_comment_prefixes=['#'])
parser.read('./redox-api.config')
redcap_api_endpoint = parser.get('REDCAP', 'LOCAL_REDCAP_URL')
redcap_api_token = parser.get('REDCAP', 'LOCAL_REDCAP_API_KEY')

# Redcap configuration
redcap = Redcap(redcap_api_endpoint, redcap_api_token)

# Verify which Redcap project we are about to perform testing on
info = redcap.project.export_project_info()
title = info['project_title']
logger.info(f'About to perform testing (including adding fake participants) on project {title}.')
s = input('Enter the name of the project to continue: ')
if s != title:
    logger.info('User input does not match project title. Exiting.')
    exit()

# Create test participants
with open('test_data.json', 'r') as fh:
    test_participants = json.load(fh)

if len(test_participants) > 0:
    ids = redcap.project.import_records(test_participants, return_content='ids', force_auto_number=False)
    logger.info(ids)
else:
    logger.debug('No test data loaded')