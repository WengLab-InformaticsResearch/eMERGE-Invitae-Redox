import logging
from datetime import date
from difflib import SequenceMatcher
from collections import namedtuple

import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class MrnMatch:
    cuimc_mrn: str = ''
    omop_person_id: int = 0
    dob: date = pd.NaT

    def __init__(self, cuimc_mrn, omop_person_id, dob):
        self.cuimc_mrn = cuimc_mrn
        self.omop_person_id = omop_person_id
        self.dob = dob

    def __str__(self):
        return f'MRN: {self.cuimc_mrn}\tOMOP: {self.omop_person_id}\tdob: {self.dob}'


GiraLabs = namedtuple('GiraLabs', ['dbp', 'sbp', 'hdl', 'cho', 'tri', 'a1c'])


class OmopExtractor:
    def __init__(self, sql_conn):
        self.sql_conn = sql_conn

        logger.debug('Initializing')
        self.initialize_eczema_conditions()
        self.initialize_wheeze_conditions()

    def find_patients_by_mrn(self, mrn: str):
        ''' Finds all persons matching the MRN
        '''
        sql = """
        SELECT *
        FROM mappings.patient_mappings pm
        JOIN person p ON pm.person_id = p.person_id
        WHERE LOCAL_PT_ID = ? AND FACILITY_CODE = ?"""

        # Determine which facility_code should be used based on length of MRN
        if len(mrn) == 7:
            facility_code = 'P'
        elif len(mrn) == 8:
            facility_code = 'A'
        elif len(mrn) == 10:
            facility_code = 'UI'
        else:
            logger.warning(f'Received an MRN with an unhandled format: {mrn}')
            return list()

        df_persons = pd.read_sql(sql, self.sql_conn, params=[mrn, facility_code])

        matches = list()
        for index, row in df_persons.iterrows():
            match = MrnMatch(mrn, row.person_id, row.birth_datetime.date())
            logger.debug(match)
            matches.append(match)
        return matches


    def find_closest_patient(self, mrn: str, dob: date):
        ''' Finds the person with a mathcing MRN and the clostest matching birthdate by string similarity

        Returns
        -------
        (MrnMatch, DOB string similarity) if a match is found, else (None, 0)
        '''
        if type(dob) is not date:
            raise TypeError

        mrn_matches = self.find_patients_by_mrn(mrn)
        closest_match = None
        max_dob_sim = 0
        if len(mrn_matches) > 0:
            for match in mrn_matches:
                if match.dob == dob:
                    # Found matching MRN and DOB, return it
                    logger.debug('Found exact matching birthdate')
                    return match, 1
                else:
                    dob_sim = SequenceMatcher(None, str(match.dob), str(dob)).ratio()
                    if dob_sim > max_dob_sim:
                        max_dob_sim = dob_sim
                        closest_match = match

            logger.debug(f'{closest_match}\tdob_sim: {dob_sim}')
            return closest_match, dob_sim
        else:
            logger.debug('No matches found')
            return None, 0


    @staticmethod
    def _check_positive_allergy_test(r, debug=False):
        def _internal(r):
            # For kU/L, using "moderate" threshold as specified in Sheldon J, Miller L. Allergy diagnosis reference guide. Clinical Biochemistry, East Kent University Hospitals, NHS. October 2014. P-6.
            # https://www.mtw.nhs.uk/wp-content/uploads/2015/08/Allergy_diagnosis_reference_guide.pdf
            custom_range_high = {
                9058: 0.70,
            }

            # Use the value_as_concept_id for positive (45884084) or detected (45877985)
            if r.value_as_concept_id is not None and not np.isnan(r.value_as_concept_id):
                return 'positive (value_as_concept_id)' if r.value_as_concept_id in (45884084, 45877985) else 'negative (value_as_concept_id)'

            # Check certain values of value_source_value
            v = r.value_source_value.strip()
            if v is None or len(v) == 0:
                return 'negative (empty value_source_value)'
            if v[0] == '<':
                # value_source_value often starts with "<" when measurement is below detection threshold
                return 'negative (value_source_value begins with "<")'
            if v[0] == '>':
                # value_source_value is sometimes above measurement limits (e.g., >100.00)
                return 'positive (value_source_value begins with ">")'
            if v.lower()[:5] == 'posit':
                # value_source_value is "positive"
                return 'positive (value_source_value is "positive")'

            # Check the quantitative measurement against the normal range
            f = None
            if r.value_as_number is not None and not np.isnan(r.value_as_number):
                f = r.value_as_number
            else:
                try:
                    f = float(v)
                except ValueError:
                    f = None

            if f is not None:
                # Compare against range_high
                if r.range_high is not None and not np.isnan(r.range_high):
                    return 'positive (value > range_high)' if f > r.range_high else 'negative (value <= range_high)'

                # Use custom range_high based on units
                if r.unit_concept_id in custom_range_high:
                    rh = custom_range_high[r.unit_concept_id]
                    return f'positive (value > custom range high ({rh}))' if f > rh else f'negative (value <= custom range high ({rh}))'

                return 'negative (numeric value, but unhandled scenario)'

            return 'negative (unhandled scenario)'

        result = _internal(r)
        if not debug:
            result = result[:5] == 'posit'
        return result


    def count_positive_allergy_tests(self, person_id, debug=False):
        allergy_test_omop_ids = [3007757, 3037831, 3016459, 3006734, 3014480, 3010354, 3023543, 3008374, 3043730, 3006606, 3002527, 3024149, 3028352, 3015561, 3015627, 3012262, 3027873, 3024593, 3023430, 3014133, 3008136, 3040439, 3020960, 3001915, 3036780, 3023351, 3036780, 3024159, 3016997, 3012711, 3016997, 3014599, 3018352, 3015123, 3012494, 1175134, 3009165, 3001488, 3025260, 3002187, 3003888, 3014126, 3038205, 3011951, 3005136, 3013101, 40768481, 3013766, 3011197, 3019658]
        allergy_test_omop_ids_str = ','.join([str(c) for c in allergy_test_omop_ids])

        # Get allergy measurements
        sql = f"""
        SELECT measurement_concept_id, measurement_type_concept_id, value_as_number, value_as_concept_id,
            unit_concept_id, range_low, range_high, measurement_source_value, measurement_source_concept_id,
            unit_source_value, value_source_value
        FROM measurement
        WHERE person_id = ? AND measurement_concept_id IN ({allergy_test_omop_ids_str})
        """
        df = pd.read_sql(sql, self.sql_conn, params=[person_id])

        # Check which measurements are positive
        df['result'] = df.apply(OmopExtractor._check_positive_allergy_test, axis=1, result_type='reduce')

        # Count unqiue positive tests (different allergens)
        pos_tests = list(df.measurement_concept_id[df.result].unique())
        return len(pos_tests)


    def initialize_eczema_conditions(self):
        sql = """
        DROP TABLE IF EXISTS #ecz_icd_mappings;

        SELECT c_icd.concept_id AS icd_concept_id, c_std.concept_id as std_concept_id
        INTO #ecz_icd_mappings
        FROM concept c_icd
        JOIN concept_relationship cr ON cr.concept_id_1 = c_icd.concept_id AND cr.relationship_id = 'Maps to'
        JOIN concept c_std ON cr.concept_id_2 = c_std.concept_id
        WHERE
            (c_icd.concept_code IN ('691', '054.0', '373.31', '380.22', '380.23', '684', '686.8', '690.12', '691.8', '693.1', '693.1', '695.89', '696.8', '703.8', '704.8', '709.9', 'V13.3')
            AND c_icd.vocabulary_id = 'icd9cm')
            OR
            ((c_icd.concept_code LIKE 'L2%' OR c_icd.concept_code LIKE 'L30%' OR c_icd.concept_code IN ('B00.0', 'H01.13', 'H60.54', 'H60.6', 'H60.8X', 'L73.8', 'L98.9', 'Z87.2'))
            AND c_icd.vocabulary_id = 'icd10cm');

        DROP TABLE IF EXISTS #ecz_icd_concept_ids;

        SELECT DISTINCT icd_concept_id AS concept_id
        INTO #ecz_icd_concept_ids
        FROM #ecz_icd_mappings;

        DROP TABLE IF EXISTS #ecz_std_concept_ids;

        SELECT DISTINCT std_concept_id AS concept_id
        INTO #ecz_std_concept_ids
        FROM #ecz_icd_mappings;
        """
        self.sql_conn.execute(sql)


    def initialize_wheeze_conditions(self):
        sql = """
        DROP TABLE IF EXISTS #whe_icd_mappings;

        SELECT c_icd.concept_id AS icd_concept_id, c_std.concept_id as std_concept_id
        INTO #whe_icd_mappings
        FROM concept c_icd
        JOIN concept_relationship cr ON cr.concept_id_1 = c_icd.concept_id AND cr.relationship_id = 'Maps to'
        JOIN concept c_std ON cr.concept_id_2 = c_std.concept_id
        WHERE
            (c_icd.concept_code IN ('466.0', '490', '491.9', '519.8', '786.07', '786.07', 'V12.69') -- leaving out 995.3 for "allergy_unspecified"
            AND c_icd.vocabulary_id = 'icd9cm')
            OR
            ((c_icd.concept_code LIKE 'T78%' OR c_icd.concept_code IN ('R06.2', 'J20.9', 'J40', 'J42', 'J98.8', 'R06.2', 'Z87.898'))
            AND c_icd.vocabulary_id = 'icd10cm');

        DROP TABLE IF EXISTS #whe_icd_concept_ids;

        SELECT DISTINCT icd_concept_id AS concept_id
        INTO #whe_icd_concept_ids
        FROM #whe_icd_mappings;

        DROP TABLE IF EXISTS #whe_std_concept_ids;

        SELECT DISTINCT std_concept_id AS concept_id
        INTO #whe_std_concept_ids
        FROM #whe_icd_mappings;
        """
        self.sql_conn.execute(sql)


    def eczema_events(self, person_id, delta_threshold=1):
        sql = f"""
        SELECT co.condition_start_date AS date,
            DATEDIFF(day, p.birth_datetime, co.condition_start_datetime) / 365.24 AS age,
            co.condition_source_concept_id
        FROM condition_occurrence co
        JOIN #ecz_std_concept_ids sc ON sc.concept_id = co.condition_concept_id
        JOIN #ecz_icd_concept_ids ic ON ic.concept_id = co.condition_source_concept_id
        JOIN person p ON co.person_id = p.person_id
        WHERE p.person_id = ?
            AND (DATEDIFF(day, p.birth_datetime, co.condition_start_datetime) / 365.24) < 18
        ORDER BY condition_start_datetime ASC;
        """
        df = pd.read_sql(sql, self.sql_conn, params=[person_id])

        events = list()
        if df is not None and len(df) > 0:
            if df.loc[0, 'age'] < 3:
                event1 = df.loc[0, :]
                events.append(event1)

                df['delta'] = df.apply(lambda x: (x.date - event1.date).days, axis=1)
                df_2 = df[df.delta >= delta_threshold].reset_index(drop=True)

                if df_2 is not None and len(df_2) > 0 and df_2.loc[0, 'age'] < 18:
                    event2 = df_2.loc[0, :]
                    events.append(event2)

        return events


    def wheeze_events(self, person_id, delta_threshold=1):
        sql = f"""
        SELECT co.condition_start_date AS date,
            DATEDIFF(day, p.birth_datetime, co.condition_start_datetime) / 365.24 AS age,
            co.condition_source_concept_id
        FROM condition_occurrence co
        JOIN person p ON co.person_id = p.person_id
        JOIN #whe_std_concept_ids sc ON sc.concept_id = co.condition_concept_id
        JOIN #whe_icd_concept_ids ic ON ic.concept_id = co.condition_source_concept_id
        WHERE p.person_id = ?
            AND (DATEDIFF(day, p.birth_datetime, co.condition_start_datetime) / 365.24) < 18
        ORDER BY condition_start_datetime ASC;
        """
        df = pd.read_sql(sql, self.sql_conn, params=[person_id])

        events = list()
        if df is not None and len(df) > 0:
            if df.loc[0, 'age'] < 3:
                event1 = df.loc[0, :]
                events.append(event1)

                df['delta'] = df.apply(lambda x: (x.date - event1.date).days, axis=1)
                df_2 = df[df.delta >= delta_threshold].reset_index(drop=True)

                if df_2 is not None and len(df_2) > 0 and df_2.loc[0, 'age'] < 18:
                    event2 = df_2.loc[0, :]
                    events.append(event2)

        return events

    def _measurement_extractor(self, person_id, measurement_concept_ids, unit_concept_ids, range_low=None, range_high=None, check_etl=True):
        sql = f"""
        SELECT TOP 1 m.measurement_concept_id, c.concept_name,
            m.measurement_date, m.value_as_number
        FROM measurement m
        JOIN concept c ON m.measurement_concept_id = c.concept_id
        WHERE person_id = ?
            AND measurement_concept_id IN ({','.join(['?'] * len(measurement_concept_ids))})
            AND unit_concept_id IN ({','.join(['?'] * len(unit_concept_ids))})
            AND value_as_number IS NOT NULL
        """
        params = [person_id] + measurement_concept_ids + unit_concept_ids

        if range_low is not None:
            sql += f" AND value_as_number >= ? "
            params.append(range_low)
        if range_high is not None:
            sql += f" AND value_as_number <= ? "
            params.append(range_high)
        if check_etl:
            sql += " AND value_source_value NOT LIKE '<%' AND value_source_value NOT LIKE '>%' "

        sql += " ORDER BY measurement_datetime DESC;"
        df = pd.read_sql(sql, self.sql_conn, params=params)

        return None if df.empty else df.iloc[0, :]


    def extract_diastolic_bp(self, person_id):
        return self._measurement_extractor(person_id=person_id,
                                    measurement_concept_ids=[3012888],
                                    unit_concept_ids=[8876],
                                    range_low=None,
                                    range_high=None)


    def extract_systolic_bp(self, person_id):
        return self._measurement_extractor(person_id=person_id,
                                    measurement_concept_ids=[3004249],
                                    unit_concept_ids=[8876],
                                    range_low=None,
                                    range_high=None)


    def extract_hdl(self, person_id):
        return self._measurement_extractor(person_id=person_id,
                                    measurement_concept_ids=[3034482, 3013473, 3053286, 3033190, 3033638, 3011884, 3023602, 3007070],
                                    unit_concept_ids=[8840],
                                    range_low=None,
                                    range_high=None)


    def extract_ldl(self, person_id):
        return self._measurement_extractor(person_id=person_id,
                                    measurement_concept_ids=[3028288, 3035899, 3028437, 3009966],
                                    unit_concept_ids=[8840],
                                    range_low=None,
                                    range_high=None)


    def extract_cholesterol_total(self, person_id):
        return self._measurement_extractor(person_id=person_id,
                                    measurement_concept_ids=[3015548, 3027114, 3031776, 3027074, 3019900, 3049873],
                                    unit_concept_ids=[8840],
                                    range_low=None,
                                    range_high=None)


    def extract_triglyceride(self, person_id):
        return self._measurement_extractor(person_id=person_id,
                                    measurement_concept_ids=[3007943, 3022192, 3022038, 3030875, 3012391, 3025839, 42868692, 3019038, 3027997, 3048773],
                                    unit_concept_ids=[8840],
                                    range_low=None,
                                    range_high=None)


    def extract_a1c(self, person_id):
        return self._measurement_extractor(person_id=person_id,
                                    measurement_concept_ids=[3004410, 3003309, 3005673, 40762352, 3007263, 3034639, 42869630, 40765129],
                                    unit_concept_ids=[8554],
                                    range_low=None,
                                    range_high=None)


    def extract_gira_labs(self, person_id):
        dbp = self.extract_diastolic_bp(person_id)
        sbp = self.extract_systolic_bp(person_id)
        hdl = self.extract_hdl(person_id)
        # ldl = self.extract_ldl(person_id)
        cho = self.extract_cholesterol_total(person_id)
        tri = self.extract_triglyceride(person_id)
        a1c = self.extract_a1c(person_id)
        return GiraLabs(dbp, sbp, hdl, cho, tri, a1c)
