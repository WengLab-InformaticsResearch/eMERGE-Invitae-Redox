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
    

# Run
`python batch_order.py`