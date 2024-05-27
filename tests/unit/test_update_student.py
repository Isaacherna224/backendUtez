import pytest

from update_data_student import app


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body": '{ "test": "prueba unitaria en update_data_student"}',
        "resource": "/{proxy+}",
    }


def test_lambda_handler(apigw_event):
    ret = app.lambda_handler(apigw_event, "")
    assert ret["statusCode"] == 200
