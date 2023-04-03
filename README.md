**This is currently under development**

# About
This project provides Python scripts to place orders with Invitae for eMERGE participants. This project is configured 
to primarily use information from a local REDCap instance, but also pulls some information from R4. Patient 
demographics are pulled from local REDCap. Baseline patient health history is pulled from local REDCap to answer
AOE (Ask at Order Entry) questions regarding primary indication and patient symptoms. The MeTree JSON file is pulled
from R4 to fill in family history of disease. A custom instrument in local REDCap is used to indicate when a 
participant is ready for order submission. 


# Configuration
1.  Install python requirements:  
    `pip install -r requirements.txt`
1.  Enter REDCap and Redox configuration settings in `redox-api.config`
1.  Enter the following static information into `redox/json_templates/new_order_template.json`:
    1.  `Meta.Destinations` (different destinations for dev/staging/prod environments in Redox)
    1.  `Meta.FacilityCode`
    1.  `Patient.Demographics.PhoneNumber` - use your site contact information
    1.  `Patient.Demographics.Address` - use your site contact information
    1.  `Order.Provider`
1.  Make other site-specific configuration changes, including, but not limited to:
    1.  Create an ordering instrument in your local REDCap. For reference, a REDCap instrument file is included in 
        `misc/redcap-instrument-redox-invitae.zip`.
    1.  In `redcap_invitae.py`, update `FIELD_RECORD_ID` to the name of the REDCap record ID field for your project
1.  There are a few safety checkpoints in place during development to reduce the chance of sensitive data being transmitted:
    1.  When `redox-api.config` has `DEVELOPMENT = True`, in `batch_order.py`:
        1.  Names of the REDCap projects will be printed, and the user will be prompted to continue 
        1.  Names of participants collected for order submission will be printed, and the user will be prompted to continue
    1.  In `invitae.py`, `SEND_REDOX` is set to `False` by default and will prevent actual order submission. Order info will
        be printed to logs for verification. The code will behave as though orders were successfully submitted. 
        Set `SEND_REDOX` to `True` to enable sending orders. 
    

# Run
`python batch_order.py`


# Contributing sources
* https://github.com/emerge-ehri/invitae-redox-orders (private repo)
* https://github.com/stormliucong/eIV-recruitement-support-redcap
