import json
import unittest
from insert_user_pool import app

mock_body = {
    "body": json.dumps({
        "email": "isaachernandez@utez.edu.mx",
        "user_name": "utez123",
        "phone_number": "+527772200022",
        "name": "Isaac Hernandez Flores",
        "age": 32,
        "gender": "M"
    })
}


class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock_body, None)
        print(result)
