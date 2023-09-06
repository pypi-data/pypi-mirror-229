import os
from ast import literal_eval
from urllib.request import urlopen
import json
from team_requests import list_decisions
from team_requests import get_decision_value
from team_requests import update_decision_value
from team_requests import USER_URL_BASE


class DecisionLab:
    def __init__(self, *, uuid=None, token=None, auth_type='USER'):
        self.auth_type = auth_type
        if uuid is None and (token or auth_type == 'TEAMS'):
            self.team_token = token or os.environ.get('DECISION_LAB_TEAM_TOKEN')
            if not self.team_token:
                raise ValueError(
                    "Team token must be provided or set as an environment variable 'DECISION_LAB_TEAM_TOKEN'")
        else:
            self.uuid = uuid or os.environ.get('DECISION_LAB_UUID')

    def list_decisions(self, private=False, private_definition='_CONFIGURATION'):
        if self.auth_type == 'TEAMS':
            return list_decisions(self.team_token, private=private,
                                  private_definition=private_definition)
        url = f'{USER_URL_BASE}/{self.uuid}'
        with urlopen(url) as response:
            data = response.read().decode()
            return json.loads(data)

    def update_decision_value(self, decision_name, value):
        return update_decision_value(decision_name, value, self.team_token)

    def get_decision(self, decision_name):
        if self.auth_type == 'TEAMS':
            return get_decision_value(decision_name, self.team_token)
        url = f'{USER_URL_BASE}/{self.uuid}/{decision_name}'
        with urlopen(url) as response:
            data = response.read().decode()
            response_json = json.loads(data)

        # Check if the response contains an error message
        if isinstance(response_json, dict) and response_json.get('success') is False:
            return []

        # Safely evaluate the response if it is a string representation of a literal
        if isinstance(response_json, str):
            try:
                response_json = literal_eval(response_json)
            except (ValueError, SyntaxError):
                pass  # Keep the response as a string if it cannot be evaluated as a literal

        return response_json
