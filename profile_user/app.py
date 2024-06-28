import json


def lambda_handler(event, __):
    body_parameters = json.loads(event["body"])
    print(body_parameters)
    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Profile User access successful"})
    }
