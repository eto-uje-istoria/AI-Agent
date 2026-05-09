import ast
import operator
from typing import Any

from app.tools.base import ToolExecutionResult


_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float | int:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return node.value

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_BINARY_OPERATORS:
            raise ValueError(f"Unsupported operator: {operator_type.__name__}")

        left = _eval_node(node.left)
        right = _eval_node(node.right)

        return _ALLOWED_BINARY_OPERATORS[operator_type](left, right)

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_UNARY_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {operator_type.__name__}")

        operand = _eval_node(node.operand)

        return _ALLOWED_UNARY_OPERATORS[operator_type](operand)

    raise ValueError(f"Unsupported expression: {type(node).__name__}")


async def calculator(expression: str) -> ToolExecutionResult:
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree)

        return ToolExecutionResult(
            content={
                "expression": expression,
                "result": result,
            }
        )
    except Exception as exc:
        return ToolExecutionResult(
            content={
                "expression": expression,
                "error": str(exc),
            }
        )


CALCULATOR_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a safe arithmetic expression. Supports +, -, *, /, %, ** and parentheses.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression, for example: '25 * 4' or '(10 + 5) / 3'.",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
}
