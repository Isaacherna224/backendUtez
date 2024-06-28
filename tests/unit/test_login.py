from login import app
import unittest
import json

mock_body = {
    "body": json.dumps({
        "username": "admin123",
        "password": "7qG#UQD0YPaa"
    })
}


class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock_body, None)
        print(result)
