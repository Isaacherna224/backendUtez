import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import json
from typing import Any, Dict
from .connection_bd import connect_to_db, execute_query, close_connection
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


def lambda_handler(event, __):
    path_parameters = event.get('pathParameters', {})
    id_param = path_parameters.get('id')
    if id_param is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Id is required."})
        }
    """
    Lambda function handler to retrieve all data from the 'class' table.

    Args:
        event (dict): Event data passed to the Lambda function.
        __ (LambdaContext): Runtime information of the Lambda function.

    Returns:
        dict: Response containing the results of the query or an error message.
    """
    # Retrieve database credentials from AWS Secrets Manager
    secret_name = os.environ['SECRET_NAME']
    region_name = os.environ['REGION_NAME']
    secret = get_secret(secret_name, region_name)

    # Database connection parameters
    host = secret['host']
    user = secret['username']
    password = secret['password']
    database = os.environ['DATA_BASE']

    # Query to select all data from the 'class' table
    query = f"SELECT * FROM class where id= {id_param}"

    # Establish database connection
    connection = connect_to_db(host, user, password, database)

    if connection:
        try:
            # Execute the query
            results = execute_query(connection, query)

            # Close the connection
            close_connection(connection)

            if results:
                # If results are obtained, log them
                logging.info("Results:")
                for row in results:
                    logging.info(row)

                # Return success response with data
                return {
                    "statusCode": 200,
                    "body": json.dumps({"data": results})
                }
            else:
                # Return empty response if no results found
                return {
                    "statusCode": 204,
                    "body": json.dumps({"message": "No results found."})
                }
        except Exception as e:
            # Log and return error response
            logging.error("Error executing query: %s", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "An error occurred while processing the request."})
            }
    else:
        # Return error response if connection failed
        logging.error("Connection to the database failed.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to connect to the database."})
        }


def get_secret(secret_name: str, region_name: str) -> Dict[str, str]:
    """
    Retrieves the secret value from AWS Secrets Manager.

    Args:
        secret_name (str): The name or ARN of the secret to retrieve.
        region_name (str): The AWS region where the secret is stored.

    Returns:
        dict: The secret value retrieved from AWS Secrets Manager.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logging.error("Failed to retrieve secret: %s", e)
        raise e

    return json.loads(get_secret_value_response['SecretString'])
