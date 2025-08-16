import time
import schedule
from datetime import datetime
from lambda_function import lambda_handler


def run_lambda_job():
    """
    Function to simulate the AWS Lambda function locally.
    """
    print(f"Running Lambda job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CST")
    # Mock event and context for local testing
    test_event = {}
    test_context = type(
        "Context",
        (),
        {
            "function_name": "crypto-dashboard-updater",
            "memory_limit_in_mb": 128,
            "invoked_function_arn": "arn:aws:lambda:us-east-2:123456789012:function:crypto-dashboard-updater",
            "aws_request_id": "test-request-id",
        },
    )()

    # Call the Lambda function
    result = lambda_handler(test_event, test_context)
    print("Lambda function result:")
    print(result)


# Schedule the job to run daily at 9:00 PM CST
schedule.every().day.at("21:58").do(run_lambda_job)

print("Scheduler started. Waiting for the next scheduled job...")

# Keep the script running to execute the scheduled job
while True:
    schedule.run_pending()
    time.sleep(1)
