import json
import os
import random
import string
import boto3
from botocore.exceptions import ClientError
from connection_bd import connect_to_db, execute_query, close_connection
import logging
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, __):
    try:
        # Validación de la entrada
        body_parameters = json.loads(event.get("body", "{}"))
        email = body_parameters.get('email')
        phone_number = body_parameters.get('phone_number')
        name = body_parameters.get('name')
        age = body_parameters.get('age')
        gender = body_parameters.get('gender')
        user_name = body_parameters.get('user_name')

        if not all([email, phone_number, name, age, gender, user_name]):
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing or invalid input parameters"})
            }

        # Generación de contraseña temporal
        try:
            password = generate_temporary_password()
        except Exception as e:
            logging.error("Error generating temporary password: %s", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Internal Server Error while generating password"})
            }

        role = "usuario"

        # Configura el cliente de Cognito
        try:
            client = boto3.client('cognito-idp', region_name='us-east-1')
            user_pool_id = "us-east-1_rIROKIgIL"
        except Exception as e:
            logging.error("Error configuring Cognito client: %s", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Internal Server Error while configuring Cognito"})
            }

        # Creación de usuario en Cognito
        try:
            client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=user_name,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'false'},
                ],
                TemporaryPassword=password
            )

            client.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username=user_name,
                GroupName=role
            )
        except ClientError as e:
            logging.error("ClientError when creating user in Cognito: %s", e)
            return {
                "statusCode": 400,
                "body": json.dumps({"error_message": e.response['Error']['Message']})
            }
        except Exception as e:
            logging.error("Unexpected error when creating user in Cognito: %s", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Internal Server Error while creating user in Cognito"})
            }

        # Inserta los datos en la base de datos
        try:
            insert_db(email, phone_number, name, age, gender, password, user_name)
        except Exception as e:
            logging.error("Error inserting data into the database: %s", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Internal Server Error while inserting data into the database"})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "User created successfully, verification email sent."})
        }

    except Exception as e:
        logging.error("Unhandled exception in lambda_handler: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({"message": "Internal Server Error", "error": str(e)})
        }



def insert_db(email, phone_number, name, age, gender, password, user_name):
    # Obtener las credenciales de la base de datos desde AWS Secrets Manager
    secret_name = 'DB_SECRET_NAME'
    db_credentials = get_db_credentials(secret_name)

    connection = connect_to_db(
        host=db_credentials['host'],
        user=db_credentials['user'],
        password=db_credentials['password'],
        database=db_credentials['database']
    )

    try:
        query = f"""
        INSERT INTO users (email, phone_number, name, age, gender, password, user_name)
        VALUES ('{email}', '{phone_number}', '{name}', {age}, '{gender}', '{password}', '{user_name}')
        """
        execute_query(connection, query)
        logging.info("Data inserted successfully into the database.")
    except Exception as e:
        logging.error("Error inserting data into the database: %s", e)
        raise e
    finally:
        close_connection(connection)


def generate_temporary_password(length=12):
    """Genera una contraseña temporal segura"""
    try:
        special_characters = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+= '
        characters = string.ascii_letters + string.digits + special_characters

        while True:
            # Genera una contraseña aleatoria
            password = ''.join(random.choice(characters) for _ in range(length))

            # Verifica los criterios
            has_digit = any(char.isdigit() for char in password)
            has_upper = any(char.isupper() for char in password)
            has_lower = any(char.islower() for char in password)
            has_special = any(char in special_characters for char in password)

            if has_digit and has_upper and has_lower and has_special and len(password) >= 8:
                return password

    except Exception as e:
        logging.error("Error generating temporary password: %s", e)
        raise e


def get_db_credentials(secret_name):
    """
    Obtiene las credenciales de la base de datos desde AWS Secrets Manager.

    :param secret_name: Nombre del secreto en AWS Secrets Manager
    :return: Diccionario con las credenciales de la base de datos (host, user, password, database)
    """
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        # Desencripta el secreto usando la clave KMS asociada
        secret = get_secret_value_response['SecretString']
        secret_dict = json.loads(secret)

        return {
            "host": secret_dict.get("host"),
            "user": secret_dict.get("username"),
            "password": secret_dict.get("password"),
            "database": secret_dict.get("dbname")
        }

    except Exception as e:
        logging.error("Error retrieving secrets from AWS Secrets Manager: %s", e)
        raise e