from set_password import app
import unittest
import json


mock_body = {
    "body": json.dumps({
        "username": "admin123",
        "temporary_password": "l|SH83Ol",
        "new_password": "7qG#UQD0YPaa"
    })
}


class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock_body, None)
        print(result)
