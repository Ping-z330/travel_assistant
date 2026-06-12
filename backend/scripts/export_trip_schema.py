import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.models.trip import TripPlan, TripPlanRequest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_path = repo_root / "shared" / "schema" / "trip.schema.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Travel Assistant Trip Contract",
        "models": {
            "TripPlanRequest": TripPlanRequest.model_json_schema(),
            "TripPlan": TripPlan.model_json_schema(),
        },
    }

    output_path.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
