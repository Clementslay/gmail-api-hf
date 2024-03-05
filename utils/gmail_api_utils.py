from .gmail_utils import GmailUtils

import requests
import json

from constants import *


class GmailAPIUtils(GmailUtils):

    def mark_message_as_read(self, message_id):
        self.modify_message(message_id, remove_label=UNREAD)

    def mark_message_as_unread(self, message_id):
        self.modify_message(message_id, add_label=UNREAD)

    def move_message_to_label(self, message_id, label_name):
        self.modify_message(message_id, add_label=label_name)

    def modify_message(self, message_id, add_label=None, remove_label=None):
        url = f"""https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/modify"""

        payload = {}

        if add_label:
            payload['addLabelIds'] = [add_label.upper()]

        if remove_label:
            payload['removeLabelIds'] = [remove_label.upper()]

        headers = {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-Type': "application/json"
        }

        print(f"POST {url}. Payload: {json.dumps(payload)}")

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        print(f"Status: {response.status_code}. Response: {response.text}")

        if not response.ok:
            response.raise_for_status()

        print(f"""Successfully modified message: `{message_id}`{f". Label added: `{add_label}`" if add_label else ""}{f". Label removed: `{remove_label}`" if remove_label else ""}""")

        return response.json()
