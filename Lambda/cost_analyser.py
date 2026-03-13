import pandas as pd
import boto3
import json
import os
from datetime import datetime
from config.aws_config import AWS_REGION, S3_BUCKET

# Create S3 client
s3 = boto3.client("s3", region_name=AWS_REGION)


# Load dataset
def load_data():
    df = pd.read_csv("../data/sample_dataset.csv")
    return df


# Analyze cost by service
def analyze_cost(df):
    service_cost = df.groupby("service")["cost"].sum()
    return service_cost


# Detect idle EC2 instances
def detect_idle(df):
    idle = df[(df["service"] == "EC2") & (df["cpu_usage"] < 5)]
    return idle["resource_id"].unique()


# Generate FinOps report
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


# Save report locally
def save_local_report(report):

    os.makedirs("../Reports/Reports", exist_ok=True)

    file_path = "../Reports/Reports/cost_report.json"

    with open(file_path, "w") as f:
        json.dump(report, f, indent=4)

    print("Local report saved:", file_path)


# Upload report to S3
def upload_report(report):

    filename = "cost_report_" + str(datetime.utcnow()) + ".json"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=json.dumps(report)
    )

    print("Report uploaded to S3:", filename)


# Main execution
if __name__ == "__main__":

    report = generate_report()

    print(report)

    save_local_report(report)

    upload_report(report)