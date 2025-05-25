import os
from dotenv import load_dotenv
import subprocess
import argparse

load_dotenv()

parser = argparse.ArgumentParser(description='Run Terraform apply or destroy')
parser.add_argument('--destroy', action='store_true', help='Run terraform destroy instead of apply')
args = parser.parse_args()

command = "destroy" if args.destroy else "apply"

subprocess.run([
    "terraform", command,
    f"-var=yandex_token={os.getenv('YANDEX_TOKEN')}",
    f"-var=cloud_id={os.getenv('CLOUD_ID')}",
    f"-var=folder_id={os.getenv('FOLDER_ID')}",
    f"-var=pg_password={os.getenv('PG_PASSWORD')}",
    "-auto-approve"
])