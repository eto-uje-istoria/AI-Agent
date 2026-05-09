import json
import time
from pathlib import Path
from typing import Any

import httpx

SCENARIOS_DIR = Path("tests/scenarios")
REPORTS_DIR = Path("reports")
REPORTS_PATH = REPORTS_DIR / "scenarios_result.json"


def load_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []

    for path in sorted(SCENARIOS_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as file:
            scenario = json.load(file)

        scenario["_path"] = str(path)
        scenarios.append(scenario)

    return scenarios


def check_response(
        scenario: dict[str, Any],
        response_json: dict[str, Any],
        latency_seconds: float,
) -> list[str]:
    expected = scenario.get("expected", {})
    errors: list[str] = []

    answer = response_json.get("answer", "")
    used_tools = response_json.get("used_tools", [])
    sources = response_json.get("sources", [])

    used_tool_names = [tool.get("name") for tool in used_tools]

    must_use_tool = expected.get("must_use_tool")
    if must_use_tool and must_use_tool not in used_tool_names:
        errors.append(
            f"Expected tool {must_use_tool!r}, got {used_tool_names!r}"
        )
    
    if expected.get("must_not_use_tools") and used_tool_names:
        errors.append(
            f"Expected no tools, got {used_tool_names!r}"
        )

    contains_any = expected.get("answer_contains_any", [])
    if contains_any:
        answer_lower = answer.lower()

        if not any(item.lower() in answer_lower for item in contains_any):
            errors.append(
                f"Answer does not contain any of {contains_any!r}"
            )
        
        if expected.get("must_have_sources") and not sources:
            errors.append(
                f"Expected sources, got empty sources list"
            )

        max_latency = expected.get("max_latency_seconds")
        if max_latency is not None and latency_seconds > max_latency:
            errors.append(
                f"Latency {latency_seconds:.2f}s exceeded max {max_latency:.2f}s"
            )

    return errors
    

def main() -> None:
    scenarios = load_scenarios()
    results: list[dict[str, Any]] = []

    with httpx.Client(timeout=120) as client:
        for scenario in scenarios:
            started_at = time.perf_counter()

            response = client.post(
                "http://localhost:8000/chat",
                json={
                    "message": scenario["message"],
                    "conversation_id": f"scenario-{scenario['name']}",
                }
            )

            latency_second = time.perf_counter() - started_at

            try:
                response_json = response.json()
            except json.JSONDecodeError:
                response_json = {"raw": response.text}

            if response.status_code != 200:
                errors = [f"HTTP {response.status_code}: {response.text}"]
            else:
                errors = check_response(
                    scenario=scenario,
                    response_json=response_json,
                    latency_seconds=latency_second,
                )

            passed = not errors

            result = {
                "name": scenario["name"],
                "path": scenario["_path"],
                "passed": passed,
                "latency_seconds": round(latency_second, 3),
                "errors": errors,
                "response": response_json,
            }

            results.append(result)

            status = "PASS" if passed else "FAIL"
            print(f"{status} {scenario['name']} ({latency_second:.2f}s)")

            for error in errors:
                print(f"  - {error}")

    summary = {
        "total": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }

    REPORTS_DIR.mkdir(exist_ok=True)

    with REPORTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print()
    print(f"Passed: {summary['passed']}/{summary['total']}")
    print(f"Report saved to {REPORTS_PATH}")


if __name__ == "__main__":
    main()
