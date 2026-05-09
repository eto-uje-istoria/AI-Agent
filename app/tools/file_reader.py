from pathlib import Path
from typing import Any

from app.config import settings
from app.schemas import Source
from app.tools.base import ToolExecutionResult


def _resolve_safe_path(path: str) -> Path:
    data_dir = Path(settings.data_dir).resolve()
    target_path = (data_dir / path).resolve()

    if not target_path.is_relative_to(data_dir):
        raise ValueError("Access outside DATA_DIR is not allowed.")
    
    relative_path = target_path.relative_to(data_dir).as_posix()
    
    return target_path, relative_path


async def file_reader(path: str) -> ToolExecutionResult:
    try: 
        target_path, relative_path = _resolve_safe_path(path)

        if not target_path.exists():
            return ToolExecutionResult(
                content={
                    "path": relative_path,
                    "error": "File does not exist.",
                }
            )

        if not target_path.is_file():
            return ToolExecutionResult(
                content={
                    "path": relative_path,
                    "error": "Path is not a file.",
                }
            )
        
        text = target_path.read_text(encoding="utf-8")

        return ToolExecutionResult(
            content={
                "path": relative_path,
                "text": text,
            },
            sources=[
                Source(
                    title=target_path.name,
                    path=str(relative_path),
                )
            ],
        )
    except Exception as exc:
        return ToolExecutionResult(
            content={
                "path": path,
                "error": str(exc),
            }
        )
    

FILE_READER_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "file_reader",
        "description": (
            "Read a UTF-8 text file from the configured DATA_DIR directory. "
            "The path must be relative to DATA_DIR. "
            "If the user mentions 'sample.txt', pass path='sample.txt'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Relative path inside DATA_DIR. "
                        "Example: if the user asks to read sample.txt, pass exactly 'sample.txt'."
                    ),
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
}
