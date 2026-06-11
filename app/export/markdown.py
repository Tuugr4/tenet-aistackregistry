SECTIONS = [
    ("provider", "Providers", ["name", "kind", "base_url"]),
    ("model", "Models", ["name", "model_id", "modality", "context_window", "license"]),
    ("prompt", "Prompts", ["name", "version", "status", "hash"]),
    ("dataset", "Datasets", ["name", "version", "license", "source_url"]),
    ("fine_tune", "Fine-tunes", ["name", "job_id", "base_model_id", "result_model_id"]),
    ("embedding_index", "Embedding Indexes", ["name", "dimension", "metric"]),
    ("vector_db", "Vector DBs", ["name", "kind", "endpoint", "collection"]),
    ("eval_result", "Eval Results", ["name", "target_type", "passed"]),
]


def _cell(value) -> str:
    if value is None:
        return "-"
    return str(value)


def to_markdown(aibom: dict) -> str:
    app = aibom["application"]
    lines = [
        f"# AIBOM Report: {app['name']}",
        "",
        f"- **Slug:** {app['slug']}",
        f"- **Environment:** {app['environment']}",
        f"- **Owner:** {_cell(app.get('owner'))}",
        f"- **Generated:** {aibom['generated_at']}",
        "",
    ]
    for kind, title, columns in SECTIONS:
        entries = aibom["components"].get(kind, [])
        if not entries:
            continue
        lines.append(f"## {title}")
        lines.append("")
        header = [*columns, "role"]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))
        for entry in entries:
            row = [_cell(entry.get(col)) for col in header]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    return "\n".join(lines)
