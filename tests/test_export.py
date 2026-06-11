async def seed(client):
    application = (
        await client.post(
            "/api/v1/applications",
            json={"name": "Support Bot", "slug": "support-bot", "environment": "prod"},
        )
    ).json()
    provider = (
        await client.post(
            "/api/v1/providers",
            json={"name": "openai", "base_url": "https://api.openai.com"},
        )
    ).json()
    model = (
        await client.post(
            "/api/v1/models",
            json={
                "name": "GPT-4o mini",
                "model_id": "gpt-4o-mini",
                "provider_id": provider["id"],
                "context_window": 128000,
            },
        )
    ).json()
    prompt = (
        await client.post(
            "/api/v1/prompts",
            json={
                "name": "answer-ticket",
                "version": "3",
                "template": "Answer politely: {ticket}",
                "variables": ["ticket"],
                "status": "prod",
            },
        )
    ).json()
    vector_db = (
        await client.post(
            "/api/v1/vector-dbs",
            json={"name": "kb", "kind": "qdrant", "collection": "kb-articles"},
        )
    ).json()

    app_id = application["id"]
    for ctype, cid, role in [
        ("provider", provider["id"], None),
        ("model", model["id"], "chat"),
        ("prompt", prompt["id"], "system"),
        ("vector_db", vector_db["id"], "retrieval"),
    ]:
        r = await client.post(
            f"/api/v1/applications/{app_id}/links",
            json={"component_type": ctype, "component_id": cid, "role": role},
        )
        assert r.status_code == 201, r.text
    return application


async def test_links_validation(client):
    application = await seed(client)
    app_id = application["id"]

    r = await client.get(f"/api/v1/applications/{app_id}/links")
    assert len(r.json()) == 4

    r = await client.post(
        f"/api/v1/applications/{app_id}/links",
        json={
            "component_type": "model",
            "component_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert r.status_code == 404


async def test_native_export(client):
    application = await seed(client)
    r = await client.get(f"/api/v1/applications/{application['id']}/aibom")
    assert r.status_code == 200
    bom = r.json()
    assert bom["aibom_version"] == "1.0"
    assert bom["application"]["slug"] == "support-bot"
    assert len(bom["components"]["model"]) == 1
    assert bom["components"]["model"][0]["role"] == "chat"
    assert bom["components"]["prompt"][0]["version"] == "3"


async def test_cyclonedx_export(client):
    application = await seed(client)
    r = await client.get(
        f"/api/v1/applications/{application['id']}/aibom", params={"format": "cyclonedx"}
    )
    assert r.status_code == 200
    bom = r.json()
    assert bom["bomFormat"] == "CycloneDX"
    assert bom["specVersion"] == "1.6"
    assert bom["serialNumber"].startswith("urn:uuid:")
    assert bom["metadata"]["component"]["type"] == "application"

    types = {c["type"] for c in bom["components"]}
    assert "machine-learning-model" in types
    assert "data" in types
    assert len(bom["services"]) == 2


async def test_markdown_report(client):
    application = await seed(client)
    r = await client.get(f"/api/v1/applications/{application['id']}/report.md")
    assert r.status_code == 200
    assert "text/markdown" in r.headers["content-type"]
    text = r.text
    assert "# AIBOM Report: Support Bot" in text
    assert "## Models" in text
    assert "gpt-4o-mini" in text
