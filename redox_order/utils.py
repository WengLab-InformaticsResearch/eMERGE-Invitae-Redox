from collections import OrderedDict
import json
import logging

from redcap_invitae import Redcap

logger = logging.getLogger(__name__)


CHECKBOX_POSITIVE_VALUES = ['1', 'checked']


def convert_emerge_race_to_redox_race(participant_data):
    """ Converts eMERGE race_at_enrollment to Redox Patient.Demographics.race values

    Note: R4 allows multiple race options. If more than one race option is selected, 'Other Race'
    is returned. If nothing is selected, 'Unknown' is returned. 

    Params
    ------
    participant_data: Dict of participant data containing race_at_enrollment values, e.g., 
                      'race_at_enrollment___1': '1'
                      Handles both raw (e.g., '0', '1') and label (e.g., 'Unchecked', 'Checked') formats

    Returns
    -------
    (String) First matching race. If no match found, return 'Unknown'
    """
    mappings = {
        'race_at_enrollment___1': 'American Indian or Alaska Native',
        'race_at_enrollment___2': 'Asian',
        'race_at_enrollment___3': 'Black or African American',
        'race_at_enrollment___4': 'Other Race',
        'race_at_enrollment___5': 'Other Race',
        'race_at_enrollment___6': 'Native Hawaiian or Other Pacific Islander',
        'race_at_enrollment___7': 'White',
        'race_at_enrollment___8': 'Other Race',
        'race_at_enrollment___9': 'Prefer not to answer',
    }
    no_match_race = 'Unknown'
    multiple_race = 'Other Race'

    redox_races = []
    for race_variable, redox_race in mappings.items():
        if race_variable in participant_data:
            race_value = participant_data[race_variable].lower()
            if race_value == '1' or race_value == 'checked':
                redox_races.append(redox_race)

    n_races = len(redox_races)
    if n_races == 0:
        return no_match_race
    elif n_races == 1:
        return redox_races[0]
    else:
        return multiple_race


def convert_emerge_race_to_invitae_ancestry(participant_data):
    """ Converts eMERGE participant data to Invitae ancestry options

    From R4, uses: race_at_enrollment, ashkenazi_jewish_ancestors

    Params
    ------
    participant_data: Dict of participant data containing race_at_enrollment values, e.g., 
                      'race_at_enrollment___1': '1'
                      Handles both raw (e.g., '0', '1') and label (e.g., 'Unchecked', 'Checked') formats

    Returns
    -------
    List of matching ancestry options
    """
    race_mappings = {
        'race_at_enrollment___1': 'Native American',
        'race_at_enrollment___2': 'Asian',
        'race_at_enrollment___3': 'Black/African-American',
        'race_at_enrollment___4': 'Hispanic',
        # 'race_at_enrollment___5': None,  # No good mapping from "Middle Eastern or North African" to Invitae ancestry options
        'race_at_enrollment___6': 'Pacific Islander',
        'race_at_enrollment___7': 'White/Caucasian',
        'race_at_enrollment___8': 'Other',
        'race_at_enrollment___9': 'Unknown',        
    }
    var_ashkenazi = 'ashkenazi_jewish_ancestors'
    invitae_ashkenazi = 'Ashkenazi Jewish'

    ancestries = []

    # R4:race_at_enrollment
    for race_variable, invitae_ancestry in race_mappings.items():
        if race_variable in participant_data:
            race_value = participant_data[race_variable].lower()
            if race_value in ('1', 'checked'):
                ancestries.append(invitae_ancestry)

    # R4: ashkenazi_jewish_ancestors
    if participant_data.get(var_ashkenazi, '').lower() in ('1', 'yes'):
        ancestries.append(invitae_ashkenazi)

    return ancestries


def map_redcap_sex_to_redox_sex(redcap_sex):
    """ Map REDCap values for sex to Redox defined values

    "Intersex" is mapped to "Other"

    Params
    ------
    redcap_sex: (string) REDCap raw data

    Returns
    -------
    (string) Redox sex value
    """
    map = {
        '1': 'Female',
        '2': 'Male',
        '3': 'Other',  # REDCap: Intersex
        '4': 'Unknown',  # REDCap: Prefer not to answer
        '': 'Unknown'  # REDCap: (question not answered)
    }
    return map[redcap_sex]


def get_invitae_primary_indication(record):
    """ Choose a primary indication for Invitae API order

    Looks as participant's personal health history response in baseline survey. Chooses the closest
    primary indication based on participant's current and past health history, ignoring conditions
    the participant indicates they are at risk for. For healthy participants, "Other" is chosen. 

    Params
    ------
    record: Dict of participant's records containing values from personal health history checkboxes, e.g., 
            'prostate_cancer___1': '1'
            Handles both raw (e.g., '0', '1') and label (e.g., 'Unchecked', 'Checked') formats

    Returns
    -------
    (String) First relevant primary indication. For healthy participants or no match found, return 'Other'
    """
    mappings = OrderedDict([
        ('prostate_cancer', 'Prostate Cancer'),
        ('pancreatic_cancer', 'Pancreatic Cancer'),
        ('breast_cancer', 'Other Cancer'),
        ('ovarian_cancer', 'Other Cancer'),
        ('colorectal_cancer', 'Other Cancer'),
        ('atrial_fibrillation', 'Cardiology: Arrhythmia'),
        ('coronary_heart_disease', 'Cardiology: Other'),
        ('heart_failure', 'Cardiology: Other'),
    ])    
    checkbox_suffix = '___1'
    past_modifier = '_2'
    
    for emerge_variable_base, invitae_indication in mappings.items():
        # check if this participant has the condition: 
        # 1) currently 
        if record[emerge_variable_base + checkbox_suffix].lower() in CHECKBOX_POSITIVE_VALUES:
            return invitae_indication
        # 2) past
        if record[emerge_variable_base + past_modifier + checkbox_suffix].lower() in CHECKBOX_POSITIVE_VALUES:
            return invitae_indication
        
    # Use 'Other' for all other scenarios
    return 'Other'


def describe_patient_history(record):
    """ Creates a description of patient history for Invitae Order

    Looks as participant's personal health history response in baseline survey and creates a written description

    Params
    ------
    record: Dict of participant's records containing values from personal health history checkboxes, e.g., 
            'prostate_cancer___1': '1'
            Handles both raw (e.g., '0', '1') and label (e.g., 'Unchecked', 'Checked') formats

    Returns
    -------
    (String) Written description of current and past conditions.
    """
    mappings = {
        Redcap.FIELD_BPHH_HYPERTENSION: 'hypertension',
        Redcap.FIELD_BPHH_HYPERLIPID: 'hypercholesterolemia',
        Redcap.FIELD_BPHH_T1DM: 'type 1 diabetes',
        Redcap.FIELD_BPHH_T2DM: 'type 2 diabetes',
        Redcap.FIELD_BPHH_KD: 'weak or failing kidneys or kidney disease',
        Redcap.FIELD_BPHH_ASTHMA: 'asthma',
        Redcap.FIELD_BPHH_OBESITY: 'obesity',
        Redcap.FIELD_BPHH_SLEEPAPNEA: 'sleep apnea',
        Redcap.FIELD_BPHH_CHD: 'coronary heart disease',
        Redcap.FIELD_BPHH_HF: 'heart failure',
        Redcap.FIELD_BPHH_AFIB: 'atrial fibrillation',
        Redcap.FIELD_BPHH_BRCA: 'breast cancer',
        Redcap.FIELD_BPHH_OVCA: 'ovarian cancer',
        Redcap.FIELD_BPHH_PRCA: 'prostate cancer',
        Redcap.FIELD_BPHH_PACA: 'pancreatic cancer',
        Redcap.FIELD_BPHH_COCA: 'colorectal cancer'
    }
    checkbox_suffix = '___1'
    past_modifier = '_2'
    
    current_conditions = list()
    past_conditions = list()
    for emerge_variable_base, description in mappings.items():
        # check if this participant has the condition: 
        # 1) currently 
        if record[emerge_variable_base + checkbox_suffix].lower() in CHECKBOX_POSITIVE_VALUES:
            current_conditions.append(description)
        # 2) past
        if record[emerge_variable_base + past_modifier + checkbox_suffix].lower() in CHECKBOX_POSITIVE_VALUES:
            past_conditions.append(description)
        
    description = ''
    if current_conditions:
        description += f"Current conditions: {', '.join(current_conditions)}. "
    if past_conditions:
        description += f"Past conditions: {', '.join(past_conditions)}."
    return description    


def generate_family_history(metree):
    """ Creates a description of family history for Invitae Order

    Looks as participant's MeTree JSON data and generates text description of family history

    Params
    ------
    metree: MeTree data. If metree passed in as string, will try to load JSON data. Otherwise, expect list of dicts.

    Returns
    -------
    (String) Written description of family history.
    """
    history = list()

    if type(metree) is str:
        metree = json.loads(metree)
    elif type(metree) is not list:
        raise TypeError

    # Create description for each person
    for record in metree:
        # Create description for each condition
        conditions = list()
        for condition in record['conditions']:
            cstr = condition['id']
            # If the condition id is "other" and meta.other has info, use that
            if cstr == 'other':
                other = condition['meta'].get('other', '')
                if other:
                    cstr = other
            age = condition['age']
            if age:
                cstr += f' (age {str(age)})'
            conditions.append(cstr)

        # Create summary of conditions
        if conditions:
            conditions_str = '; '.join(conditions)
        else:
            # If medicalHistory is not empty, use that as the summary. 
            # It may be things like "healthy" or "unknown"
            mh = record['medicalHistory']
            if mh:                
                conditions_str = mh
            else:
                conditions_str = 'no conditions listed'
        history.append(f"{record['relation']}: {conditions_str}.")

    return ' '.join(history)


# testing
if __name__ == "__main__":
    # Create template
    d_template = {'ashkenazi_jewish_ancestors': ''}
    for i in range(1, 10):
        d_template[f'race_at_enrollment___{i}'] = '0'

    print('################ test convert_emerge_race_to_redox_race ################')

    # Test with nothing filled
    print('\nTest with nothing')
    r = convert_emerge_race_to_redox_race(d_template)
    print(r)
    
    # Test single option
    print('\nTest single race')
    for i in range(1, 10):
        d = d_template.copy()
        d[f'race_at_enrollment___{i}'] = '1'
        r = convert_emerge_race_to_redox_race(d)
        print(f'{i}: {r}')

    # Test joint Hispanic and 1 race 
    print('\nTest hispanic + single race')
    d_template_3 = d_template.copy()
    d_template_3['race_at_enrollment___4'] = '1'
    for i in range(1, 10):
        d = d_template_3.copy()
        d[f'race_at_enrollment___{i}'] = '1'
        r = convert_emerge_race_to_redox_race(d)
        print(f'{i}: {r}')

    
    print('################ test convert_emerge_race_to_invitae_ancestry ################')    
    
    # Test with nothing filled
    print('\nTest with nothing')
    a = convert_emerge_race_to_invitae_ancestry(d_template)
    print(a)

    # Test single option
    print('\nTest single race')
    for i in range(1, 10):
        d = d_template.copy()
        d[f'race_at_enrollment___{i}'] = '1'
        a = convert_emerge_race_to_invitae_ancestry(d)
        print(f'{i}: {a}')

    # Test joint ashkenazi jewish and 1 race 
    print('\nTest ashkenazi jewish + single race')
    d_template_2 = d_template.copy()
    d_template_2['ashkenazi_jewish_ancestors'] = '1'
    for i in range(1, 10):
        d = d_template_2.copy()
        d[f'race_at_enrollment___{i}'] = '1'
        a = convert_emerge_race_to_invitae_ancestry(d)
        print(f'{i}: {a}')

    # Test joint Hispanic and 1 race 
    print('\nTest hispanic + single race')
    d_template_3 = d_template.copy()
    d_template_3['race_at_enrollment___4'] = '1'
    for i in range(1, 10):
        d = d_template_3.copy()
        d[f'race_at_enrollment___{i}'] = '1'
        a = convert_emerge_race_to_invitae_ancestry(d)
        print(f'{i}: {a}')

    print('################ test get_invitae_primary_indication ################')    
    d_template = {(x+'___1'):'0' for x in Redcap.FIELDS_BPHH}
    for f in Redcap.FIELDS_BPHH:
        d = d_template.copy()
        d[f+'___1'] = '1'
        x = get_invitae_primary_indication(d)
        print(f'{f}: {x}')

    print('################ test describe_patient_history with individual conditions ################')    
    d_template = {(x+'___1'):'0' for x in Redcap.FIELDS_BPHH}
    for f in Redcap.FIELDS_BPHH:
        d = d_template.copy()
        d[f+'___1'] = '1'
        x = describe_patient_history(d)
        print(f'{f}: {x}')

    print('################ test describe_patient_history with random selection of conditinos ################')    
    d_template = {(x+'___1'):'0' for x in Redcap.FIELDS_BPHH}
    n = len(Redcap.FIELDS_BPHH)
    import random
    for i in range(10):
        d = d_template.copy()
        n_conditions = random.randint(1, 10)
        sample = random.sample(range(n), n_conditions)
        fields = [Redcap.FIELDS_BPHH[i]+'___1' for i in sample]
        for f in fields:            
            d[f] = '1'            
        x = describe_patient_history(d)
        print(f'fields: {fields}\ndescription: {x}\n--------------\n')
