import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv

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
    
def get_user_progress_from_s3(file_key):
    try:
        # Get the file object from S3
        s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
        
        # Read the contents of the file
        file_content = s3_object['Body'].read().decode('utf-8')
        
        # Process the file lines as before
        user_progress = [x.strip() for x in file_content.splitlines()]

        return user_progress
    
    except Exception as e:
        print(f"Error fetching file from S3: {e}")
        return []