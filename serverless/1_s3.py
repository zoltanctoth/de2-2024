# Import required libraries
import os
import pprint
import random
import string

import boto3
from dotenv import load_dotenv

# Load AWS credentials from .env file
load_dotenv()

# Initialize pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

# Create S3 client with credentials from environment variables
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-west-1",  # Ireland region
)

# List all buckets in your AWS account
response = s3.list_buckets()
print("Raw response:")
pp.pprint(response)

print("\nJust the bucket names:")
for bucket in response["Buckets"]:
    print(f"- {bucket['Name']}")


# Function to create a unique bucket name
def generate_bucket_name(base_name):
    """Generate a unique bucket name using base name and random digits"""
    random_part = "".join(random.choices(string.digits, k=3))
    return f"{base_name}-{random_part}"


# IMPORTANT: Replace this with your name
my_name = "add-your-name-here"  # TODO: Change this!
bucket_name = generate_bucket_name(my_name)
print(f"Generated bucket name: {bucket_name}")

# Get the default region and create bucket
default_region = "eu-west-1"
print(f"Creating bucket in region: {default_region}")

try:
    # Note: Bucket configuration is required for all regions except us-east-1
    bucket_configuration = {"LocationConstraint": default_region}
    response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=bucket_configuration)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        print(f"✅ Bucket {bucket_name} created successfully in {default_region}")
        print("\nFull response:")
        pp.pprint(response)
except Exception as e:
    print(f"❌ Error creating bucket: {str(e)}")

# Create a sample file
sample_content = """Hello from AWS S3!
This is a sample file created during the tutorial.
You can modify this content to upload different text."""

try:
    with open("my_content.txt", "w") as file:
        file.write(sample_content)
    print("✅ Sample file created locally")
except Exception as e:
    print(f"❌ Error creating file: {str(e)}")

# Upload file to S3
try:
    s3.upload_file("my_content.txt", bucket_name, "my_content.txt")
    print(f"✅ File uploaded successfully to: s3://{bucket_name}/my_content.txt")
except Exception as e:
    print(f"❌ Error uploading file: {str(e)}")

# Download file from S3
try:
    s3.download_file(bucket_name, "my_content.txt", "my_content_downloaded.txt")
    print("✅ File downloaded successfully")

    # Display the contents
    with open("my_content_downloaded.txt", "r") as file:
        print("\nFile contents:")
        print("-" * 20)
        print(file.read())
        print("-" * 20)
except Exception as e:
    print(f"❌ Error downloading file: {str(e)}")


# Function to clean up all resources
def cleanup_resources():
    """Clean up all resources created during this tutorial"""
    try:
        # 1. Delete the object from S3
        print(f"Deleting object from S3 bucket...")
        s3.delete_object(Bucket=bucket_name, Key="my_content.txt")
        print("✅ S3 object deleted")

        # 2. Delete the bucket
        print(f"Deleting bucket {bucket_name}...")
        s3.delete_bucket(Bucket=bucket_name)
        print("✅ S3 bucket deleted")

        # 3. Delete local files
        local_files = ["my_content.txt", "my_content_downloaded.txt"]
        for file in local_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"✅ Deleted local file: {file}")

        print("\n✅ All cleanup completed successfully!")

    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")


# Run cleanup
cleanup_resources()
