import time

import httpx


def main() -> None:
    started_at = time.perf_counter()

    with httpx.stream(
        "POST",
        "http://localhost:8000/chat/stream",
        json={
            "message": "Напиши подробное объяснение LangGraph на 30 предложений с примерами."
        },
        timeout=120,
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                elapsed = time.perf_counter() - started_at
                print(f"+{elapsed:.3f}s {line}")


if __name__ == "__main__":
    main()