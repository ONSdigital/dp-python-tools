from dpytools.secrets.secret import _NO_RESPONSE_ERROR, Secret


def test_sets_none_error():
    id = "Should be set"
    secret = Secret(response=None, id=id)

    assert secret.value is None
    assert secret.id == id
    assert secret.error == _NO_RESPONSE_ERROR
