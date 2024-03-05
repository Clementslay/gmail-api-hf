import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from custom_exceptions import *

from datetime import datetime
import re


class GmailUtils:

    def __init__(self):
        print("Establishing connection to Gmail service..")

        self.service = None
        self.creds = None

        SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]
        self.creds = None

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        self.service = build("gmail", "v1", credentials=self.creds)

        print("Service established successfully")


    def get_all_emails(self, full_email_list=None, next_page_token=None):

        print(f"Getting emails. Page Token: {next_page_token}")

        if full_email_list is None:
            full_email_list = []

        results = self.service.users().messages().list(userId='me', maxResults=5, pageToken=next_page_token).execute()

        email_list = results.get('messages', [])

        for email in email_list:
            email_response = self.get_email_by_id(email['id'])
            email = self.populate_email_fields(email_response, email)

        full_email_list += email_list

        if 'nextPageToken' in results:
            self.get_all_emails(full_email_list=full_email_list, next_page_token=results['nextPageToken'])

        return full_email_list

    def get_email_by_id(self, message_id):
        print(f"Getting email by ID:{message_id}")
        return self.service.users().messages().get(userId='me', id=message_id).execute()

    def populate_email_fields(self, email_response, email):

        print(f"Populating email fields for table entry. Message ID: {email['id']}")
        
        email_headers = email_response['payload']['headers']

        del email['threadId']

        email['from'] = self.get_email_address_from_sender(self.get_value_from_email_header(value='From', email_headers=email_headers))
        email['to'] = self.get_value_from_email_header(value='To', email_headers=email_headers)
        email['subject'] = self.get_value_from_email_header(value='Subject', email_headers=email_headers)
        email['date_received'] = self.convert_epoch_to_datetime(email_response['internalDate'])

        return email

    def get_email_address_from_sender(self, sender):
        if email_address_match := re.findall(r'<(.*?)>', sender):
            return email_address_match[0]
        return sender

    def get_value_from_email_header(self, value, email_headers):
        try:
            return list(filter(lambda header: header['name'] == value, email_headers))[0]['value']

        except Exception:
            raise GmailSDKError(f"Unable to fetch `{value}` from email header.")

    def convert_epoch_to_datetime(self, epoch_time):
        return (datetime.fromtimestamp(int(epoch_time) / 1000)).strftime('%Y-%m-%d %H:%M:%S')
