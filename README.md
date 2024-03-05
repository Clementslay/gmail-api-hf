# Gmail APIs - HF
 This project consists of standalone Python scripts that would do the following operations -
 1. Fetch emails through Google's Gmail SDK for Python.
 2. Load these emails into an SQLite3 database.
 3. Based on the `rules.json` file perform some actions to certain emails based on a set of conditions

## Environment
- Python 3.10.x

## Installation
1. Clone the repository
2. Install packages listed in `requirements.txt`
   ```
   pip install -r requirements.txt
   ```
3. Set up your Gmail API credentials:

   - Follow the instructions in the [Python Quickstart guide](https://developers.google.com/gmail/api/quickstart/python) to enable the Gmail API and obtain your `credentials.json` file.
   - Place the `credentials.json` file in the root directory of this project.
4. Run `fetch_emails.py`
   - When executed for the first time, since the `token.json` file does not exist, you will be redirected to a URL to authorize the Google OAuth application.
   - After successful authorization, the script would fetch all the emails available in the Gmail account.
   - Each email's complete response will be fetched which consists of information such as the sender, recipient, subject, date received, etc.
   - These entries will then be loaded into the DB - `hf_gmail.db` under the `message` table.
5. Add rules into the `rules.json` file
  - The rules must be added as a dictionary to the `rules` list. For example,
    ```
    {
    "rules": [
        {
            "description": "Rule 1",
            "predicate": "all",
            "conditions": [
                {
                    "field_name": "from",
                    "predicate": "contains",
                    "value": "tenmiles.com"
                },
                {
                    "field_name": "subject",
                    "predicate": "contains",
                    "value": "interview"
                },
                {
                    "field_name": "date_received",
                    "predicate": "lesser than",
                    "value": "2",
                    "unit": "days"
                }
            ],
            "actions": [
                {
                    "action_type": "move message",
                    "message_label": "inbox"
                },
                {
                    "action_type": "mark as read"
                }
            ]
        }
    ]
    }
    ```
7. Run `process_emails.py`
   - The script will iterate through every rule that is listed in the `rules.json` file.
   - Based on the conditions & the predicate properties that are mentioned in the rule the query gets generated and executed.
   - The query results would bring up the emails that are in the `message` table that match the conditions mentioned in the rule.
   - Each resulting email will be processed based on the corresponding rule's action (Move message to a label, Mark as read/unread).
