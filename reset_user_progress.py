import boto3
from dotenv import load_dotenv
import os

load_dotenv()

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
# aws_region = os.getenv('AWS_DEFAULT_REGION')

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    # region_name=aws_region
)

BUCKET_NAME = 'anotacje-med'

# Function to list "folders" (S3 prefixes) under a specific path
def list_folders_in_s3(prefix):
    result = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')
    if 'CommonPrefixes' in result:
        return [prefix['Prefix'].split('/')[-2] for prefix in result['CommonPrefixes']]
    return []

# Function to list files in an S3 path
def list_files_in_s3(prefix):
    result = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    if 'Contents' in result:
        return [obj['Key'].split('/')[-1] for obj in result['Contents']]
    return []

# Function to delete files or folders in S3
def delete_s3_folder(prefix):
    result = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    if 'Contents' in result:
        objects_to_delete = [{'Key': obj['Key']} for obj in result['Contents']]
        s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': objects_to_delete})

# Function to create an empty file in S3 (to simulate `touch`)
def create_empty_file_in_s3(key):
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body='')

# Define the S3 paths
users_prefix = 'data/replies/'
fresh_to_touch = ["logs/", "logs/general.txt", "finished/", "packs_done.txt"]

# List users in the S3 bucket
users = list_folders_in_s3(users_prefix)

# Iterate through users and handle their folders and files
for user in users:
    user_prefix = f"{users_prefix}{user}/"
    inside = list_files_in_s3(user_prefix)

    # Delete files or folders under each user's directory
    for file in inside:
        try:
            # Deleting the file or folder
            delete_s3_folder(f"{user_prefix}/{file}")
        except Exception as e:
            print(f"Error deleting {file} in {user_prefix}: {e}")

    # Recreate fresh directories or empty files
    for f in fresh_to_touch:
        full_key = f"{user_prefix}{f}"
        if f.endswith('/'):
            # "Folder" in S3, no action needed since S3 doesn't have real directories
            pass
        else:
            # Create an empty file
            create_empty_file_in_s3(full_key)
