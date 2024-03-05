from googleapiclient.errors import HttpError

import traceback

from utils.gmail_utils import GmailUtils
from utils.sqlite_utils import SqliteUtils

def main():

    try:
        # Create Gmail API service
        gmail_sdk_utils = GmailUtils()

        # Get all emails
        email_list = gmail_sdk_utils.get_all_emails()

        # Establish DB connection
        sqlite_utils = SqliteUtils('hf_gmail.db')
        sqlite_utils.connect()

        # Create table if not available
        sqlite_utils.execute_query("""CREATE TABLE IF NOT EXISTS message (id INTEGER PRIMARY KEY, message_id TEXT, "from" TEXT, "to" TEXT, subject TEXT, date_received DATETIME)""")

        # Load emails as table entries
        sqlite_utils.execute_many("""INSERT INTO message (message_id, "from", "to", subject, date_received) VALUES (?,?,?,?,?)""", email_list)

    except HttpError as error:
        print(f"Google API error occurred: {type(error).__name__}:{error}")

    except Exception:
        print(f"Error occurred: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
