import pymysql
import logging

logging.basicConfig(level=logging.INFO)


def connect_to_db(host, user, password, database):
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        logging.info("Connection established successfully.")
        return connection
    except Exception as e:
        logging.error("Error connecting to the database: %s", e)
        return None


def execute_query(connection, query):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        logging.error("Error executing query: %s", e)
        return None


def close_connection(connection):
    if connection:
        connection.close()
        logging.info("Connection closed successfully.")
