import requests
import json
from pprint import pprint
from datetime import datetime
from io import StringIO
import pandas as pd

api_key_r4 = 'C1800890D733FBBB59AA5F0483265362'
r4_api_endpoint = 'https://redcap.vanderbilt.edu/api/'

# Get local REDCap version
data = {
    'token': api_key_r4,
    'content': 'version'
}
r = requests.post(r4_api_endpoint,data=data)
print('HTTP Status: ' + str(r.status_code))
print('survey link:' + r.text)


