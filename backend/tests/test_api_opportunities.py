"""
Tests for the /opportunities API endpoints.
"""
import pytest
from tests.conftest import make_opportunity_data


@pytest.mark.asyncio
async def test_health_check(client):
    """Health endpoint returns 200 and healthy status."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_opportunities_empty(client):
    """Empty DB returns empty results list."""
    resp = await client.get("/opportunities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_create_opportunity(client):
    """POST /opportunities creates a new opportunity."""
    payload = make_opportunity_data()
    resp = await client.post("/opportunities", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["category"] == "scholarship"
    assert data["india_eligible"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_list_opportunities_after_create(client):
    """After creating an opportunity, list returns it."""
    payload = make_opportunity_data(link="https://example.com/list-test")
    await client.post("/opportunities", json=payload)

    resp = await client.get("/opportunities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_opportunity_by_id(client):
    """GET /opportunities/{id} returns the correct opportunity."""
    payload = make_opportunity_data(link="https://example.com/get-by-id")
    create_resp = await client.post("/opportunities", json=payload)
    opp_id = create_resp.json()["id"]

    resp = await client.get(f"/opportunities/{opp_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == opp_id
    assert resp.json()["title"] == payload["title"]


@pytest.mark.asyncio
async def test_get_opportunity_not_found(client):
    """GET /opportunities/{id} returns 404 for unknown ID."""
    resp = await client.get("/opportunities/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_by_category(client):
    """Filter by category returns only matching opportunities."""
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/cat-scholarship",
        category="scholarship",
    ))
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/cat-grant",
        category="grant",
    ))

    resp = await client.get("/opportunities?category=scholarship")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert all(r["category"] == "scholarship" for r in results)


@pytest.mark.asyncio
async def test_filter_by_women_friendly(client):
    """Filter women_friendly=true returns only women-friendly opportunities."""
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/women-yes",
        women_friendly=True,
    ))
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/women-no",
        women_friendly=False,
    ))

    resp = await client.get("/opportunities?women_friendly=true")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert all(r["women_friendly"] is True for r in results)


@pytest.mark.asyncio
async def test_filter_is_expired_default_false(client):
    """Default filter excludes expired opportunities."""
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/expired",
        is_expired=True,
        deadline="2020-01-01",
    ))
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/active",
        is_expired=False,
    ))

    resp = await client.get("/opportunities?is_expired=false")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert all(r["is_expired"] is False for r in results)


@pytest.mark.asyncio
async def test_text_search(client):
    """Search parameter filters by title/description text."""
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/climate-grant",
        title="Climate Innovation Grant",
        description="Funding for climate tech startups.",
    ))
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/unrelated",
        title="Unrelated Opportunity",
        description="Nothing to do with climate.",
    ))

    resp = await client.get("/opportunities?search=climate")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert any("climate" in r["title"].lower() or "climate" in (r["description"] or "").lower()
               for r in results)


@pytest.mark.asyncio
async def test_pagination(client):
    """Pagination returns correct page slices."""
    for i in range(5):
        await client.post("/opportunities", json=make_opportunity_data(
            link=f"https://example.com/page-test-{i}",
            title=f"Paginated Opportunity {i}",
        ))

    resp = await client.get("/opportunities?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2


@pytest.mark.asyncio
async def test_patch_opportunity(client):
    """PATCH /opportunities/{id} partially updates an opportunity."""
    payload = make_opportunity_data(link="https://example.com/patch-test")
    create_resp = await client.post("/opportunities", json=payload)
    opp_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/opportunities/{opp_id}",
        json={"title": "Updated Title", "funding_amount": "$50,000"},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["title"] == "Updated Title"
    assert data["funding_amount"] == "$50,000"
   
    assert data["category"] == "scholarship"


@pytest.mark.asyncio
async def test_stats_endpoint(client):
    """GET /opportunities/stats returns aggregate counts."""
    await client.post("/opportunities", json=make_opportunity_data(
        link="https://example.com/stats-test"
    ))
    resp = await client.get("/opportunities/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "active" in data
    assert "by_category" in data
