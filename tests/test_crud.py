CASES = [
    ("/api/v1/providers", {"name": "anthropic", "kind": "api"}, {"base_url": "https://api.anthropic.com"}),
    ("/api/v1/models", {"name": "GPT-4o mini", "model_id": "gpt-4o-mini"}, {"context_window": 128000}),
    ("/api/v1/prompts", {"name": "summarize", "version": "1", "template": "Summarize: {text}"}, {"status": "prod"}),
    ("/api/v1/datasets", {"name": "support-tickets", "version": "2024-01"}, {"license": "internal"}),
    ("/api/v1/vector-dbs", {"name": "main-qdrant", "kind": "qdrant"}, {"collection": "docs"}),
]


async def test_crud_roundtrip(client):
    for url, create_body, update_body in CASES:
        r = await client.post(url, json=create_body)
        assert r.status_code == 201, (url, r.text)
        item = r.json()
        item_id = item["id"]

        r = await client.get(f"{url}/{item_id}")
        assert r.status_code == 200
        assert r.json()["name"] == create_body["name"]

        r = await client.put(f"{url}/{item_id}", json=update_body)
        assert r.status_code == 200
        for key, value in update_body.items():
            assert r.json()[key] == value

        r = await client.get(url)
        assert any(x["id"] == item_id for x in r.json())

        r = await client.delete(f"{url}/{item_id}")
        assert r.status_code == 204
        r = await client.get(f"{url}/{item_id}")
        assert r.status_code == 404


async def test_prompt_hash_and_unique_version(client):
    body = {"name": "greet", "version": "1", "template": "Hello {name}"}
    r = await client.post("/api/v1/prompts", json=body)
    assert r.status_code == 201
    first = r.json()
    assert len(first["hash"]) == 64

    r = await client.post("/api/v1/prompts", json=body)
    assert r.status_code == 409

    r = await client.put(f"/api/v1/prompts/{first['id']}", json={"template": "Hi {name}"})
    assert r.json()["hash"] != first["hash"]


async def test_fk_resources(client):
    provider = (await client.post("/api/v1/providers", json={"name": "openweights"})).json()
    model = (
        await client.post(
            "/api/v1/models",
            json={"name": "llama", "model_id": "llama-3", "provider_id": provider["id"]},
        )
    ).json()
    dataset = (await client.post("/api/v1/datasets", json={"name": "corpus"})).json()

    r = await client.post(
        "/api/v1/fine-tunes",
        json={
            "name": "llama-support",
            "base_model_id": model["id"],
            "dataset_id": dataset["id"],
            "hyperparams": {"epochs": 3},
        },
    )
    assert r.status_code == 201

    r = await client.post(
        "/api/v1/embedding-indexes",
        json={"name": "docs-index", "embedding_model_id": model["id"], "dimension": 1024},
    )
    assert r.status_code == 201

    r = await client.post(
        "/api/v1/eval-results",
        json={
            "name": "helpfulness-v2",
            "target_type": "model",
            "target_id": model["id"],
            "metrics": {"accuracy": 0.91},
            "passed": True,
        },
    )
    assert r.status_code == 201


async def test_metadata_field(client):
    r = await client.post(
        "/api/v1/providers", json={"name": "meta-test", "metadata": {"team": "ml-platform"}}
    )
    assert r.status_code == 201
    assert r.json()["metadata"] == {"team": "ml-platform"}
