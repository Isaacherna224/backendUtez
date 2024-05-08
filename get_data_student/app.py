import json


def lambda_handler(event, __):
    print(event)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "get Data Students",
        }),
    }
