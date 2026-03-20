def test_ranges_endpoint_returns_seeded_results(client) -> None:
    response = client.get("/api/v1/ranges?limit=5")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]
    assert payload["pagination"]["page_size"] == 5


def test_range_detail_returns_404_for_unknown_ticker(client) -> None:
    response = client.get("/api/v1/ranges/ZZZZ")

    assert response.status_code == 404
