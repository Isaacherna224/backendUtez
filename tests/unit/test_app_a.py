from unittest.mock import patch

from botocore.exceptions import ClientError

from get_class_by_id import app
import unittest
import json

mock_body = {
    "body": json.dumps({
        "id": 1
    })
}

mock_path = {
    "body": {
        "id": 1
    }
}


class TestApp(unittest.TestCase):

    @patch.dict("os.environ", {"REGION_NAME": "mexico", "DATA_BASE": "bd", "SECRET_NAME": "secret"})
    @patch("get_class_by_id.app.get_secret")
    @patch("get_class_by_id.app.connect_to_db")
    @patch("get_class_by_id.app.execute_query")
    @patch("get_class_by_id.app.close_connection")
    def test_lambda_handler(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        mock_get_secret.return_value = {'username': 'usuario', 'password': '1234567', 'engine': 'mysql',
                                        'host': 'host', 'port': 3306, 'dbInstanceIdentifier': 'utezbd'}
        mock_connect_to_db.return_value = True
        mock_execute_query.return_value = [{"id": 5, "grade": 1, "group": 'C', "name": 'Jose Antonio'}]
        result = app.lambda_handler(mock_body, None)
        self.assertEqual(result['statusCode'], 200)
        body = json.loads(result['body'])
        self.assertIn("data", body)
        self.assertTrue(body["data"])
        mock_close_connection.assert_called_once_with(True)

    @patch.dict("os.environ", {"REGION_NAME": "mexico", "DATA_BASE": "bd", "SECRET_NAME": "secret"})
    @patch("get_class_by_id.app.get_secret")
    @patch("get_class_by_id.app.connect_to_db")
    @patch("get_class_by_id.app.execute_query")
    @patch("get_class_by_id.app.close_connection")
    def test_lambda_handler_no_data(self, mock_close_connection, mock_execute_query, mock_connect_to_db,
                                    mock_get_secret):
        mock_get_secret.return_value = {'username': 'usuario', 'password': '123456', 'engine': 'mysql',
                                        'host': 'host', 'port': 3306, 'dbInstanceIdentifier': 'utezbd'}
        mock_connect_to_db.return_value = True
        mock_execute_query.return_value = {}
        result = app.lambda_handler(mock_body, None)
        self.assertEqual(result['statusCode'], 204)
        body = json.loads(result['body'])
        self.assertIn("message", body)
        self.assertEqual(body['message'], "No results found.")
        mock_close_connection.assert_called_once_with(True)

    @patch.dict("os.environ", {"REGION_NAME": "mexico", "DATA_BASE": "bd", "SECRET_NAME": "secret"})
    @patch("get_class_by_id.app.get_secret")
    def test_lambda_handler_get_secret_fail(self, mock_get_secret):
        mock_get_secret.side_effect = ClientError({'Error': {'Message': "Secrets Manager",
                                                             'Code': 'ResourceNotFoundException'},
                                                   'ResponseMetadata': {'RequestId': 'e95b0796', 'HTTPStatusCode': 400,
                                                                        'HTTPHeaders':
                                                                            {'x-amzn-requestid': 'e95b0796',
                                                                             'content-type': 'applicat',
                                                                             'content-length': '99',
                                                                             'date': 'Sat, 15 Jun',
                                                                             'connection': 'close'},
                                                                        'RetryAttempts': 0},
                                                   'Message': "Secrets Manager c"},
                                                  "GetSecretValue")

        result = app.lambda_handler(mock_body, None)
        self.assertEqual(result["statusCode"], 400)
        body = json.loads(result["body"])
        self.assertIn("error", body)
        self.assertEqual(body["error"], "An error occurred while processing the request get_secret")
