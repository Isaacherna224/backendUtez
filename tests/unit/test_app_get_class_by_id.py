import json
import unittest
from ...get_class_by_id import app

event_success = {
    "pathParameters": {
        "id": 1
    }
}

event_success_no_data = {
    "pathParameters": {
        "id": 1235
    }
}

event_success_no_id = {
    "pathParameters": {
    }
}


class TestAppGetClassById(unittest.TestCase):
    def test_lambda_handler_success(self):
        result = app.lambda_handler(event_success, None)
        self.assertEqual(result['statusCode'], 200)

    def test_lambda_handler_no_data(self):
        result = app.lambda_handler(event_success_no_data, None)
        self.assertEqual(result['statusCode'], 204)

    def test_lambda_handler_no_id(self):
        result = app.lambda_handler(event_success_no_id, None)
        self.assertEqual(result['statusCode'], 400)
