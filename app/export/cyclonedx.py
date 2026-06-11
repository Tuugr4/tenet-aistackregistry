import uuid

CDX_TYPES = {
    "model": "machine-learning-model",
    "fine_tune": "machine-learning-model",
    "prompt": "data",
    "dataset": "data",
    "embedding_index": "data",
    "eval_result": "data",
}

SERVICE_KINDS = ("provider", "vector_db")

SKIP_KEYS = {"id", "name", "version", "created_at", "updated_at", "metadata", "role"}


def _properties(kind: str, entry: dict) -> list[dict]:
    props = [{"name": "aibom:type", "value": kind}]
    if entry.get("role"):
        props.append({"name": "aibom:role", "value": entry["role"]})
    for key, value in entry.items():
        if key in SKIP_KEYS or value in (None, {}, []):
            continue
        props.append({"name": f"aibom:{key}", "value": str(value)})
    return props


def to_cyclonedx(aibom: dict) -> dict:
    app = aibom["application"]
    components: list[dict] = []
    services: list[dict] = []

    for kind, entries in aibom["components"].items():
        for entry in entries:
            item = {
                "bom-ref": f"{kind}:{entry['id']}",
                "name": entry["name"],
                "properties": _properties(kind, entry),
            }
            if entry.get("version"):
                item["version"] = str(entry["version"])
            if kind in SERVICE_KINDS:
                services.append(item)
            else:
                components.append({"type": CDX_TYPES[kind], **item})

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": aibom["generated_at"],
            "component": {
                "type": "application",
                "bom-ref": f"application:{app['id']}",
                "name": app["name"],
                "properties": [
                    {"name": "aibom:slug", "value": app["slug"]},
                    {"name": "aibom:environment", "value": app["environment"]},
                ],
            },
        },
        "components": components,
        "services": services,
    }
