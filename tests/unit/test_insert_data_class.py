import pytest

from insert_data_class import app


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""
    return {
        "body": '{ "test": "prueba unitaria en insert_data_class"}',
        "resource": "/{proxy+}"
    }


def test_lambda_handler(apigw_event):
    ret = app.lambda_handler(apigw_event, "")
    assert ret["statusCode"] == 200
