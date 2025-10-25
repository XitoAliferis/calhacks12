#!/usr/bin/env python3
"""Quick evaluation helper to validate AI outputs against schemas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app import schemas
from app.services import ai_service


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate prompts through the AI service")
    parser.add_argument("prompts", type=Path, help="Path to a JSON array of prompt strings")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/eval_results.json"),
        help="Where to store raw AI responses",
    )
    args = parser.parse_args()

    prompts = json.loads(args.prompts.read_text())
    if not isinstance(prompts, list):
        raise ValueError("Prompts file must be a JSON list of strings")

    aggregated: list[dict] = []
    for prompt in prompts:
        if not isinstance(prompt, str):
            raise ValueError("Each prompt must be a string")
        todos = ai_service.generate_structured_todos(prompt)
        response = schemas.AIGenerateResponse(todos=todos, persisted_ids=[])
        aggregated.append({"prompt": prompt, "todos": response.model_dump()})
        print(f"✔ Evaluated prompt: {prompt}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(aggregated, indent=2))
    print(f"Saved {len(aggregated)} responses to {args.output}")


if __name__ == "__main__":
    main()
