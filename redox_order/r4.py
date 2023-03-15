import logging
import json

from redcap import Project

logger = logging.getLogger(__name__)

class R4(Project):
    # REDCap variable names
    FIELD_RECORD_ID = 'record_id'  # Record ID in R4
    FIELD_METREE_JSON_FILE = 'metree_import_json_file'

    def __init__(self, endpoint, api_token):
        self.endpoint = endpoint
        self.api_token = api_token

        # PyCap expects endpoint to end with '/'
        if self.endpoint[-1] != '/':
            self.endpoint += '/'
        super().__init__(self.endpoint, self.api_token)

    def get_metree_json(record_id):
        """ Get MeTree JSON data file from R4

        Params
        ------
        record_id: (str) record ID

        Returns
        -------
        JSON data object if MeTree is available. Otherwise, None
        """
        try:
            file_response = self.export_file(record=record_id, field=FIELD_METREE_JSON_FILE)
        except RequestException:
            # No MeTree JSON file for this participant
            return None

        # Convert response to JSON object
        return json.loads(respfile_responseonse[0])
