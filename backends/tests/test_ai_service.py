from __future__ import annotations

import json

from app.services import ai_service


def test_mock_ai_generation(tmp_path, monkeypatch):
    sample = {"todos": [{"title": "Sample", "priority": "medium", "status": "pending", "subitems": []}]}
    mock_file = tmp_path / "mock.json"
    mock_file.write_text(json.dumps(sample))

    monkeypatch.setattr(ai_service.settings, "MOCK_AI_RESPONSES_FILE", str(mock_file))

    todos = ai_service.generate_structured_todos("ignored")
    assert len(todos) == 1
    assert todos[0].title == "Sample"
