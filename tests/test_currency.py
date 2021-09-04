def test_get_spot_prices(test_api):
    response = test_api.get("/v1/currency/")
    assert response.status_code == 200


def test_ticker(test_api):
    response = test_api.get("/v1/currency?ticker=EUR")
    assert response.status_code == 200


def test_invalid_ticker(test_api):
    response = test_api.get("/v1/currency?ticker=XXX")
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid currency"}
