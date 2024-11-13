import os
import shutil
import subprocess
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # GitHub repository details
    github_repo_url = "https://github.com/username/repo-name.git"
    repo_name = "repo-name"  # Specify the name of the repo as in GitHub
    s3_bucket = "your-bucket-name"
    s3_path = "path/to/repo"

    # Temporary directory in Lambda's /tmp folder
    local_repo_path = f"/tmp/{repo_name}"

    # Remove any existing directory to avoid conflicts
    if os.path.exists(local_repo_path):
        shutil.rmtree(local_repo_path)

    # Clone the GitHub repository into /tmp directory
    try:
        subprocess.run(["git", "clone", github_repo_url, local_repo_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return {
            'statusCode': 500,
            'body': f"Error cloning repository: {e}"
        }

    # Upload the repository files to the specified S3 bucket
    for root, dirs, files in os.walk(local_repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Generate S3 object key by stripping the /tmp/ and repo_name parts
            s3_key = os.path.join(s3_path, os.path.relpath(file_path, local_repo_path))
            try:
                s3_client.upload_file(file_path, s3_bucket, s3_key)
                print(f"Uploaded {file_path} to s3://{s3_bucket}/{s3_key}")
            except Exception as e:
                print(f"Error uploading file {file_path}: {e}")
                return {
                    'statusCode': 500,
                    'body': f"Error uploading file {file_path}: {e}"
                }

    # Clean up the temporary directory (optional)
    shutil.rmtree(local_repo_path)

    return {
        'statusCode': 200,
        'body': f"Repository {repo_name} successfully uploaded to S3 bucket {s3_bucket}."
    }
