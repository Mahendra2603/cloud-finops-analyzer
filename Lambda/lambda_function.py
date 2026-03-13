import pandas as pd
import boto3
import json
from datetime import datetime

AWS_REGION = "us-east-1"
S3_BUCKET = "finopps-bucket"

s3 = boto3.client("s3", region_name=AWS_REGION)

def load_data():
    df = pd.read_csv("..data/sample_dataset.csv")
    return df

def analyze_cost(df):
    return df.groupby("service")["cost"].sum()

def detect_idle(df):
    idle = df[(df["service"] == "EC2") & (df["cpu_usage"] < 5)]
    return idle["resource_id"].unique()

def generate_report():
    df = load_data()
    service_cost = analyze_cost(df)
    idle_instances = detect_idle(df)

    report = {
        "generated_time": str(datetime.utcnow()),
        "service_cost": service_cost.to_dict(),
        "idle_instances": list(idle_instances),
        "recommendations": [
            "stop idle instances",
            "resize compute resources",
            "remove unused storage"
        ]
    }

    return report

def upload_report(report):
    filename = "cost_report_" + str(datetime.utcnow()) + ".json"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=json.dumps(report)
    )

def lambda_handler(event, context):

    report = generate_report()

    upload_report(report)

    return {
        "statusCode": 200,
        "body": "FinOps report generated"
    }