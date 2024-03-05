import traceback

from utils.sqlite_utils import SqliteUtils
from utils.gmail_api_utils import GmailAPIUtils

import json
from constants import *


def main():

    try:
        # Load rules.json which contains the list of rules, its conditions and actions
        rules_list = get_rules()

        # Process the rules list
        process_rules(rules_list)

    except Exception:
        print(f"Error occurred: {traceback.format_exc()}")


def process_rules(rules_list):
    # Create Gmail API service (API)
    gmail_api_utils = GmailAPIUtils()

    # Establish DB connection
    sqlite_utils = SqliteUtils('hf_gmail.db')
    sqlite_utils.connect()

    # Iterate through each rule
    for rule in rules_list['rules']:
        print(f"START - rule: `{rule['description']}`")

        # Generate query to be executed based on rules
        query = generate_sql_query(rule)

        # Execute query
        query_results = sqlite_utils.execute_query(query)
        print(f"Query results: {query_results}")

        # Process messages retrieved from previous query
        process_messages(query_results, rule['actions'], gmail_api_utils)

        print(f"EXIT - rule: `{rule['description']}`")


def generate_sql_query(rule):
    query = "SELECT * FROM message WHERE "

    query_condition_list = [
        generate_query_condition(condition) for condition in rule['conditions']
    ]
    query += f'{OR if rule["predicate"] == "any" else AND}'.join(query_condition_list)

    print(f"Query generated: {query}")

    return query


def generate_query_condition(condition):

    if condition['predicate'] == CONTAINS:
        return f'''
            "{condition['field_name']}" like '%{condition['value']}%'
        '''

    if condition['predicate'] == DOES_NOT_CONTAIN:
        return f'''
            "{condition['field_name']}" not like '%{condition['value']}%'
        '''

    if condition['predicate'] == EQUALS:
        return f'''
            "{condition['field_name']}" = '{condition['value']}'
        '''

    if condition['predicate'] == DOES_NOT_EQUAL:
        return f'''
            "{condition['field_name']}" != '{condition['value']}'
        '''

    if condition['predicate'] == GREATER_THAN:
        return f'''
            datetime('now','localtime','-{condition['value']} {condition['unit']}') > "{condition['field_name']}"
        '''

    if condition['predicate'] == LESSER_THAN:
        return f'''
            datetime('now','localtime','-{condition['value']} {condition['unit']}') < "{condition['field_name']}"
        '''


def get_rules():
    rules_file = open('rules.json')
    return json.load(rules_file)


def process_messages(messages, actions, gmail_api_utils: GmailAPIUtils):

    # Iterate through each message 
    for message in messages:
        print(f"Attempting to process email: `{message['message_id']}`..")

        # Iterate through each action to be done for every message
        for action in actions:

            print(f"""Action to be done: `{action['action_type']}`{f" TO `{action['message_label']}`" if 'message_label' in action else ""}""")
            
            if action['action_type'] == MOVE_MESSAGE:
                gmail_api_utils.move_message_to_label(message['message_id'], action['message_label'])
            elif action['action_type'] == MARK_AS_READ:
                gmail_api_utils.mark_message_as_read(message['message_id'])
            elif action['action_type'] == MARK_AS_UNREAD:
                gmail_api_utils.mark_message_as_unread(message['message_id'])


if __name__ == "__main__":
    main()
