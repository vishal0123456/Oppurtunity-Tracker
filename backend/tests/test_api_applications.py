"""
Tests for the /applications API endpoints.
"""
import pytest
from tests.conftest import make_opportunity_data


async def create_test_opportunity(client, link="https://example.com/app-test-opp") -> str:
    """Helper: create an opportunity and return its ID."""
    resp = await client.post("/opportunities", json=make_opportunity_data(link=link))
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_applications_empty(client):
    """Empty tracker returns empty list."""
    resp = await client.get("/applications")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_application(client):
    """POST /applications creates a tracker entry."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-create")
    resp = await client.post("/applications", json={
        "opportunity_id": opp_id,
        "status": "saved",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "saved"
    assert data["opportunity_id"] == opp_id
    assert data["priority"] == 3  # default


@pytest.mark.asyncio
async def test_create_application_invalid_opportunity(client):
    """Creating application for non-existent opportunity returns 404."""
    resp = await client.post("/applications", json={
        "opportunity_id": "00000000-0000-0000-0000-000000000000",
        "status": "saved",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_application_duplicate(client):
    """Creating duplicate application for same opportunity returns 409."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-dup")
    await client.post("/applications", json={"opportunity_id": opp_id})
    resp = await client.post("/applications", json={"opportunity_id": opp_id})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_application_invalid_status(client):
    """Creating application with invalid status returns 400."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-bad-status")
    resp = await client.post("/applications", json={
        "opportunity_id": opp_id,
        "status": "not_a_real_status",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_update_application_status(client):
    """PUT /applications/{id} updates status."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-update")
    create_resp = await client.post("/applications", json={
        "opportunity_id": opp_id,
        "status": "saved",
    })
    app_id = create_resp.json()["id"]

    update_resp = await client.put(f"/applications/{app_id}", json={"status": "applied"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "applied"


@pytest.mark.asyncio
async def test_update_application_notes(client):
    """PUT /applications/{id} updates notes."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-notes")
    create_resp = await client.post("/applications", json={"opportunity_id": opp_id})
    app_id = create_resp.json()["id"]

    update_resp = await client.put(f"/applications/{app_id}", json={
        "notes": "Remember to attach CV",
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["notes"] == "Remember to attach CV"


@pytest.mark.asyncio
async def test_update_application_priority(client):
    """PUT /applications/{id} updates priority."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-priority")
    create_resp = await client.post("/applications", json={"opportunity_id": opp_id})
    app_id = create_resp.json()["id"]

    update_resp = await client.put(f"/applications/{app_id}", json={"priority": 1})
    assert update_resp.status_code == 200
    assert update_resp.json()["priority"] == 1


@pytest.mark.asyncio
async def test_update_application_dates(client):
    """PUT /applications/{id} updates applied_at and reminder_date."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-dates")
    create_resp = await client.post("/applications", json={"opportunity_id": opp_id})
    app_id = create_resp.json()["id"]

    update_resp = await client.put(f"/applications/{app_id}", json={
        "applied_at": "2025-06-01",
        "reminder_date": "2025-07-01",
    })
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["applied_at"] == "2025-06-01"
    assert data["reminder_date"] == "2025-07-01"


@pytest.mark.asyncio
async def test_update_application_document_links(client):
    """PUT /applications/{id} updates document_links."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-docs")
    create_resp = await client.post("/applications", json={"opportunity_id": opp_id})
    app_id = create_resp.json()["id"]

    links = "https://drive.google.com/file1\nhttps://drive.google.com/file2"
    update_resp = await client.put(f"/applications/{app_id}", json={"document_links": links})
    assert update_resp.status_code == 200
    assert update_resp.json()["document_links"] == links


@pytest.mark.asyncio
async def test_delete_application(client):
    """DELETE /applications/{id} removes the entry."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-delete")
    create_resp = await client.post("/applications", json={"opportunity_id": opp_id})
    app_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/applications/{app_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/applications/{app_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_applications_by_status(client):
    """GET /applications?status= filters correctly."""
    opp1 = await create_test_opportunity(client, "https://example.com/app-filter-1")
    opp2 = await create_test_opportunity(client, "https://example.com/app-filter-2")

    await client.post("/applications", json={"opportunity_id": opp1, "status": "applied"})
    await client.post("/applications", json={"opportunity_id": opp2, "status": "saved"})

    resp = await client.get("/applications?status=applied")
    assert resp.status_code == 200
    results = resp.json()
    assert all(r["status"] == "applied" for r in results)


@pytest.mark.asyncio
async def test_application_includes_opportunity(client):
    """Application response includes nested opportunity data."""
    opp_id = await create_test_opportunity(client, "https://example.com/app-nested")
    create_resp = await client.post("/applications", json={"opportunity_id": opp_id})
    data = create_resp.json()

    assert data["opportunity"] is not None
    assert data["opportunity"]["id"] == opp_id
