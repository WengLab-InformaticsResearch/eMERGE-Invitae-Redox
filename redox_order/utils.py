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
