import pymysql

# Variables de entorno para la configuración de RDS
rds_host = "utez.cdwwqmfwlvzd.us-east-1.rds.amazonaws.com"
rds_user = "admin"
rds_password = "Capufe037"
rds_db = "utez_db"


def create_database_and_tables():
    connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_password)

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {rds_db}")
            cursor.execute(f"USE {rds_db}")

            create_class_table = """
            CREATE TABLE IF NOT EXISTS class (
                id INT AUTO_INCREMENT PRIMARY KEY,
                grado INT NOT NULL,
                grupo VARCHAR(5) NOT NULL,
                profesor VARCHAR(45) NOT NULL
            )
            """
            cursor.execute(create_class_table)

            create_students_table = """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                id_class INT,
                FOREIGN KEY (id_class) REFERENCES class(id)
            )
            """
            cursor.execute(create_students_table)
            connection.commit()

    finally:
        connection.close()


def lambda_handler(event, context):
    create_database_and_tables()
    return {
        'statusCode': 200,
        'body': 'Database and tables created successfully.'
    }
