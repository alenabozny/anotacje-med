import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from datetime import datetime

load_dotenv()

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
# aws_region = os.getenv('AWS_DEFAULT_REGION')

import sqlite3

def get_timestamped_db_name(base_name="answers"):
    # Generate a timestamp string in the format YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.db"

def get_db_connection():
    conn = sqlite3.connect('answers.db')
    conn.row_factory = sqlite3.Row  # This returns results as dictionaries
    return conn

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    # region_name=aws_region
)

BUCKET_NAME = 'anotacje-med'

def select_all_answers():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Select all rows from the 'answers' table
    cursor.execute('SELECT * FROM answers;')
    
    # Fetch all rows
    rows = cursor.fetchall()

    # Print each row
    for row in rows:
        print(dict(row))
    
    conn.close()

def delete_all_answers():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select all rows from the 'answers' table
    cursor.execute('DELETE FROM answers;')
    conn.close()

def update_ans_dict(ct_id, ans_tpl):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the ct_id already exists in the table
    cursor.execute('''
        INSERT INTO answers (ct_id, answer) 
        VALUES (?, ?) 
        ON CONFLICT(ct_id) 
        DO UPDATE SET answer=excluded.answer
    ''', (ct_id, json.dumps(ans_tpl)))
    
    print(f"Answer for Content nr {ct_id} submitted to the database with values {ans_tpl}")
    conn.commit()
    conn.close()

def list_user_packs(username, prefix='data/sourcepacks_med/jsons_all/'):
    user_suffix = username.split('_')[-1]  # Extract suffix from username

    try:
        # List objects in the specified S3 bucket with the given prefix
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        
        # Extract file names that match the criteria
        user_packs = sorted([
            obj['Key'] for obj in response.get('Contents', [])
            if obj['Key'].endswith(f'person_{user_suffix}.json')
        ])

        return user_packs

    except NoCredentialsError:
        print("Credentials not available.")
        return []
    
def get_user_progress_from_s3(username):
    try:
        # Get the file object from S3
        s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=f"data/replies/{username}/packs_done.txt")
        
        # Read the contents of the file
        file_content = s3_object['Body'].read().decode('utf-8')
        
        # Process the file lines as before
        user_progress = [x.strip() for x in file_content.splitlines()]

        return user_progress
    
    except Exception as e:
        print(f"Error fetching file from S3: {e}")
        return []
    
import json

def load_json_from_s3(file_key):
    try:
        # Get the file object from S3
        s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
        
        # Read the file content and load it as JSON
        file_content = s3_object['Body'].read().decode('utf-8')
        contents = json.loads(file_content)

        return contents
    
    except Exception as e:
        print(f"Error loading JSON from S3: {e}")
        return {}

def upload_db_to_s3(s3_client, bucket, username, file_name='answers.db'):

    object_name = get_timestamped_db_name()
    object_name = f'data/replies/{username}/' + object_name

    try:
        # Upload the file
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded to {bucket}/{object_name}")
    except Exception as e:
        print(f"Error uploading file: {e}")

def survey_done(success_string, selected_pack, ct_id):
    st.success(success_string)
    username = st.session_state['username']

    select_all_answers()
    upload_db_to_s3(s3, BUCKET_NAME, 'anotator_0', file_name='answers.db')
    
    # Define S3 keys for the files
    # finished_key = f"data/replies/{st.session_state['username']}/finished/finished_{selected_pack}"
    packs_done_key = f"data/replies/{username}/packs_done.txt"
    logs_key = f"data/replies/{username}/logs/general.txt"

    try:
        # Upload finished survey result to S3
        # s3.put_object(Bucket=BUCKET_NAME, Key=finished_key, Body=survey.to_json().encode('utf-8'))
        # Append to the packs_done.txt file in S3
        # First, download the existing file if it exists
        try:
            packs_done_object = s3.get_object(Bucket=BUCKET_NAME, Key=packs_done_key)
            packs_done_content = packs_done_object['Body'].read().decode('utf-8')
        except s3.exceptions.NoSuchKey:
            packs_done_content = ""  # If the file doesn't exist, start with an empty string

        # Append the new entry
        packs_done_content += f"{selected_pack}\n"

        # Upload the updated content back to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=packs_done_key, Body=packs_done_content.encode('utf-8'))

        # Append to the general logs in S3
        # First, download the existing log file if it exists
        try:
            logs_object = s3.get_object(Bucket=BUCKET_NAME, Key=logs_key)
            logs_content = logs_object['Body'].read().decode('utf-8')
        except s3.exceptions.NoSuchKey:
            logs_content = ""  # If the file doesn't exist, start with an empty string

        # Append the new log entry
        log_entry = f"FINISHED Pack\t{selected_pack}\tTimestamp\t{datetime.now().strftime('%Y%m%d_%H%M%S')}\tCtID\t{ct_id}\n"
        logs_content += log_entry

        # Upload the updated logs back to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=logs_key, Body=logs_content.encode('utf-8'))

        # Switch the page after successful submission
        switch_page("main")

    except Exception as e:
        print(f"Error writing to S3: {e}")

# Function to log the survey state and activity to S3
# def log_survey_state_and_activity(survey, s_pages, selected_pack, ct_id, username):
#     try:
#         # Define S3 keys for the logs
#         last_state_key = f"data/replies/{username}/logs/{selected_pack}_last_state.txt"
#         general_log_key = f"data/replies/{username}/logs/general.txt"

#         if s_pages.current > 0:
#             # Logging current state of the survey after each question
#             # Fetch the existing last state file if it exists
#             try:
#                 last_state_object = s3.get_object(Bucket=BUCKET_NAME, Key=last_state_key)
#                 last_state_content = last_state_object['Body'].read().decode('utf-8')
#             except s3.exceptions.NoSuchKey:
#                 last_state_content = ""  # If the file doesn't exist, start with an empty string

#             # Append the new state log entry
#             last_state_content += f"--- time {time.time()} | page {s_pages.current} ---\n"
#             last_state_content += survey.to_json()

#             # Upload the updated state log back to S3
#             s3.put_object(Bucket=BUCKET_NAME, Key=last_state_key, Body=last_state_content.encode('utf-8'))

#             # Log activity (page, time, content ID)
#             # Fetch the existing general log file if it exists
#             try:
#                 general_log_object = s3.get_object(Bucket=BUCKET_NAME, Key=general_log_key)
#                 general_log_content = general_log_object['Body'].read().decode('utf-8')
#             except s3.exceptions.NoSuchKey:
#                 general_log_content = ""  # If the file doesn't exist, start with an empty string

#             # Append the new activity log entry
#             log_entry = f"Pack\t{selected_pack}\tPage\t{s_pages.current}\tTimestamp\t{time.time()}\tContentID\t{ct_id}\n"
#             general_log_content += log_entry

#             # Upload the updated activity log back to S3
#             s3.put_object(Bucket=BUCKET_NAME, Key=general_log_key, Body=general_log_content.encode('utf-8'))

#     except Exception as e:
#         print(f"Error logging survey state and activity to S3: {e}")

# import re
# import json

# def extract_entry_data(entry):
#     # Split the entry by '---' to separate the header and the JSON content
#     [header, json_part] = entry.split(' ---\n')
    
#     # Extract the timestamp and page from the header
#     timestamp, page_info = header.split(' | ')
#     timestamp = float(timestamp.strip())
    
#     # Extract the widget key IDs from the JSON
#     data_dict = json.loads(json_part.strip())
    
#     # Create a new dictionary to store the result
#     result_dict = {}
#     ct_id = ''
#     for key, value in data_dict.items():
#         # Extract the widget ID from the key (e.g., "5444_wiarygdnosc" -> "5444")
#         widget_id = value['widget_key'].split('_')[1]  # get the part before the underscore
#         result_dict[widget_id] = value['value']  # Store value and timestamp
#         ct_id = value['widget_key'].split('_')[0]
    
#     return {
#         "timestamp": timestamp,
#         "ct_id": ct_id,  # Extract the page number
#         "widgets": result_dict
#     }

# def get_last_state_per_page(survey_log_key):
#     # Split the log into individual states based on "--- time"
#     last_state_object = s3.get_object(Bucket=BUCKET_NAME, Key=survey_log_key)
#     last_state_content = last_state_object['Body'].read().decode('utf-8')
#     survey_states = re.split(r'--- time ', last_state_content)
    
#     # Dictionary to store the last state per page
#     page_state_dict = {}
    
#     # Iterate through each state entry and extract the page and JSON data
#     for entry in survey_states[1:]:  # Skip the first empty entry
#         entry_dict = extract_entry_data(entry)
#         page_state_dict[entry_dict['ct_id']] = (entry_dict['timestamp'], 
#                                                entry_dict['widgets'])


#     for key, val in page_state_dict.items():
#         print(key)
#         print(val)    
#     return page_state_dict

# get_last_state_per_page('data/replies/anotator_0/logs/0_last_state.txt')
# select_all_answers()
# upload_db_to_s3(s3, BUCKET_NAME, 'anotator_0', file_name='answers.db')