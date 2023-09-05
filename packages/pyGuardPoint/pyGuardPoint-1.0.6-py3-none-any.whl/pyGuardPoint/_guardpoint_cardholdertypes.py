from .guardpoint_dataclasses import CardholderType
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class CardholderTypesAPI:
    def get_cardholder_types(self):
        url = "/odata/API_CardholderTypes"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = self.gp_json_query("GET", headers=headers, url=url)

        if code != 200:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']
                elif 'message' in json_body:
                    error_msg = json_body['message']

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        cardholder_types = []
        for x in json_body['value']:
            cardholder_types.append(CardholderType(x))
        return cardholder_types
