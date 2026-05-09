# AI-Agent

## Architecture decisions

### Anthropic SDK vs LangGraph

В качестве слоя оркестрации для ядра агента был выбран LangGraph.

В рамках задачи рассматривались два варианта реализации: использовать Anthropic SDK напрямую или построить agent workflow через LangGraph. Anthropic SDK хорошо подходит для проектов, где основной модельный провайдер — Anthropic/Claude, а приложение завязано на Anthropic-native API. В этом проекте используется Polza.ai через OpenAI-compatible API, поэтому прямая завязка на Anthropic SDK снизила бы переносимость решения.

LangGraph выбран потому, что он позволяет описать работу агента как явный граф шагов. Текущий graph содержит вызов модели, выполнение инструментов, условную маршрутизацию по наличию tool calls и сборку финального ответа:

```text
START
  -> call_model
  -> if tool_calls: execute_tools -> call_model
  -> build_response
  -> END
```

---

### Run ruff and mypy:

```ruff check .```
or 
```ruff check app```

fix:
```ruff check . --fix```
and
```ruff format .```

mypy:
```python -m mypy app tests```
