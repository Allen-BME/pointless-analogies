import mysql.connector
import boto3
import os
import json
from aws_lambda_powertools.utilities import parameters

def initialize_database(event, context):
    # Get the credentials for the database
    secret_name = os.environ['secret_name']
    secret_dict = parameters.get_secret(secret_name, transform = "json")
    db_username = secret_dict['username']
    db_password = secret_dict['password']
    db_host = secret_dict['host']
    db_name = secret_dict['dbname']

    # Try to create the table
    try:
        connection = mysql.connector.connect(
            host = db_host,
            user = db_username,
            password = db_password,
            database = db_name
        )
        cursor = connection.cursor()

        # Create a table with columns for the image hash, first category name, second category name,
        # first category vote count, and second category vote count. IMPORTANT: The type of ImageHash
        # is not final, it should be replaced once the hash function is complete
        cursor.execute("""
            CREATE TABLE Votes (
                ImageHash CHAR(63),
                Category1 CHAR(15),
                Category2 CHAR(15),
                Category1VoteCount INT(255),
                Category2VoteCount INT(255)
        """)

        # Show the columns from the table
        cursor.execute("SHOW COLUMNS FROM Votes")
        columns = cursor.fetchall()
        print("Columns in the Votes table:")
        for column in columns:
            print(column)

        connection.commit()
        cursor.close()
        connection.close()

        return {
            "statusCode": 200,
            "body": "Database successfully initialized."
        }
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return {
            "statusCode": 500,
            "body": "Failed to connect to database"
        }






