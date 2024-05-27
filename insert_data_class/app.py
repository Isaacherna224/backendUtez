import pymysql

rds_host = "utez.cdwwqmfwlvzd.us-east-1.rds.amazonaws.com"
rds_user = "admin"
rds_password = "Capufe037"
rds_db = "utez_db"


def lambda_handler(event, __):
    grado = event['pathParameters'].get('grado')
    grupo = event['pathParameters'].get('grupo')
    profesor = event['pathParameters'].get('profesor')

    if grado is None or grupo is None or profesor is None:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters.'
        }

    insert_into_class(grado, grupo, profesor)

    return {
        'statusCode': 200,
        'body': 'Record inserted successfully.'
    }


def insert_into_class(grado, grupo, profesor):
    connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_password, db=rds_db)

    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO class (grado, grupo, profesor) VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (grado, grupo, profesor))
            connection.commit()
    finally:
        connection.close()
