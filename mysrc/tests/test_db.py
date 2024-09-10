import pytest


@pytest.mark.asyncio
async def test_connection(client):
    response = client.get("api/tenders/")
    assert response.status_code == 200
    assert len(response.json()) == 0
