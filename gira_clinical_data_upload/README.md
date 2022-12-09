# About
**Under development.**

Extracts clinical data for GIRA calculations from OMOP database, stores them in local REDCap project first.
If all values fall within an acceptable range, the clinical data will be automatically pushed to R4.
If any values fall outside an acceptable range, the participant's data will need to be reviewed first.

# Configuration
1. Install requirements:
   `pip install -r requirements.txt`
2. Copy/rename `config_template.ini` to `config.ini` and update configuration

# Run
`python gira_cde.py`

# References
1. [Implementation guide](https://docs.google.com/document/d/1S2k9Oz7XeMTuHz2qlMvsuo6Ln9LROVYg/edit#)
