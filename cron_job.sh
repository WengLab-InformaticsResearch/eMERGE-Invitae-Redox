#!/bin/bash

/home/cl3720/miniconda3/bin/python /phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/data_pull_from_r4.py \
--log /phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/data-pull.log \
--token /phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/api_tokens.json \
2> /phi_home/cl3720/phi/eMERGE/eIV-recruitement-support-redcap/errors.log