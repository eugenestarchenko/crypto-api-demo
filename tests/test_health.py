def test_main(test_api):
    response = test_api.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "Crypto API Demo ✨"}


def test_get_health(test_api):
    response = test_api.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"health": "ok"}
