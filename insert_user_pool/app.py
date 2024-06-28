import json
import os
import random
import string
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, __):
    body_parameters = json.loads(event["body"])
    email = body_parameters.get('email')
    phone_number = body_parameters.get('phone_number')
    name = body_parameters.get('name')
    age = body_parameters.get('age')
    gender = body_parameters.get('gender')
    user_name = body_parameters.get('user_name')
    password = generate_temporary_password()
    role = "usuario"

    if email is None or phone_number is None or name is None or age is None or gender is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "missing input parameters"})
        }

    try:
        # Configura el cliente de Cognito
        client = boto3.client('cognito-idp', region_name='us-east-1')
        user_pool_id = "us-east-1_rIROKIgIL"

        # Crea el usuario con correo no verificado y contraseña temporal que se envia automaticamente a su correo
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

        insert_db(email, phone_number, name, age, gender, password,user_name)

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "User created successfully, verification email sent."})
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({"error_message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error_message": str(e)})
        }


def insert_db(email, phone_number, name, age, gender, password, user_name):
    print(f"insert into table value({email},{phone_number},{name},{age},{gender},{password},{user_name})")
    return True


def generate_temporary_password(length=12):
    """Genera una contraseña temporal segura"""
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
