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
