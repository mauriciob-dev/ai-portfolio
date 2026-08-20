# 🤖 Chatbot con Function Calling (OpenAI API)

Chatbot conversacional en Python que usa la API de OpenAI con **function calling** para ejecutar herramientas reales (cálculo matemático y consulta de hora) en lugar de generar respuestas alucinadas, manteniendo memoria de contexto entre turnos.

## Por qué este proyecto

Los modelos de lenguaje pueden "sonar" correctos sin serlo — especialmente en tareas que requieren precisión (matemática, datos en tiempo real, consultas a sistemas externos). Este proyecto demuestra cómo diseñar un sistema donde el modelo **decide qué acción tomar**, pero la **ejecución real ocurre en código determinístico**, no en la generación de texto del LLM.

## Cómo funciona

1. El usuario escribe un mensaje, que se agrega al historial de conversación (`messages`).
2. Se llama a la API de OpenAI (`chat.completions.create`) pasando ese historial y la lista de `tools` disponibles.
3. El modelo responde de una de dos formas:
   - **Texto directo**, si no necesita ninguna herramienta.
   - **Una petición de tool call** (`tool_calls`): el modelo *propone* el nombre de una función y sus argumentos en formato JSON — **el modelo nunca ejecuta código**, solo solicita que se ejecute.
4. Si hay una tool call, el código Python (`run_tool`) ejecuta la función real correspondiente y captura el resultado.
5. Ese resultado se agrega al historial con `role: "tool"`, vinculado a la petición original mediante `tool_call_id`.
6. Se hace una **segunda llamada** a la API con el resultado ya incluido, y esta vez el modelo genera la respuesta final en lenguaje natural, basada en el dato real devuelto por la función.

> Cada tool usada implica **dos round-trips** al API (petición → ejecución local → respuesta final), no uno solo. Esto es relevante para entender costo y latencia en sistemas de producción.

Un `system prompt` explícito instruye al modelo a preferir siempre las herramientas sobre el cálculo mental, evitando alucinaciones en operaciones que el modelo podría "resolver" incorrectamente por su cuenta.

## Herramientas (tools) implementadas

| Tool | Descripción | Argumentos |
|---|---|---|
| `calculate` | Evalúa una expresión matemática de forma segura (sin acceso a builtins) | `expression: str` |
| `get_time` | Devuelve la fecha y hora actual del sistema | *(ninguno)* |

## Manejo de errores

El sistema maneja fallos en tres capas distintas, cada una con una estrategia de recuperación apropiada:

- **Argumentos malformados**: si el modelo genera un JSON inválido, se captura con `json.JSONDecodeError` y se informa el error sin romper el loop.
- **Fallo dentro de una tool**: cada función se ejecuta dentro de un `try/except` propio (ej. división por cero), devolviendo un mensaje de error que el modelo puede explicar al usuario.
- **Fallos de la API**: se distinguen `RateLimitError` (créditos agotados, se detiene el programa), `APIConnectionError` (problema de red, se reintenta) y `APIError` genérico (se informa y continúa).

## Stack

- Python 3.12
- [`openai`](https://github.com/openai/openai-python) — SDK oficial
- [`python-dotenv`](https://github.com/theskumar/python-dotenv) — manejo de variables de entorno

## Setup

```bash
# Clonar y entrar al proyecto
git clone <tu-repo-url>
cd 01-call-api

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Instalar dependencias
python -m pip install openai python-dotenv

# Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY
```

## Uso

```bash
python main.py
```

```
Chatbot listo. Escribe 'salir' para terminar.
Tú: cuánto es 234 * 17
Bot: 234 * 17 es igual a 3978.
Tú: dame la hora actual
Bot: La hora actual es 18:26 del 20 de agosto de 2026.
Tú: salir
```

## Estructura del proyecto

```
01-call-api/
├── main.py           # Loop principal, definición de tools y lógica de ejecución
├── .env.example       # Plantilla de variables de entorno (sin datos sensibles)
├── .gitignore          # Excluye venv/ y .env
└── README.md
```

## Aprendizajes clave

- El modelo **propone** acciones, el código **ejecuta**: la separación entre razonamiento (LLM) y ejecución (Python determinístico) es el núcleo de function calling.
- El comportamiento del modelo depende tanto del `system prompt` como del código — no forzar el uso de una tool puede resultar en respuestas "convincentes" pero no verificadas.
- Diseñar manejo de errores por capa (parseo, ejecución, red) evita que un solo tipo de fallo tumbe todo el sistema.

## Posibles mejoras (roadmap)

- [ ] Agregar streaming de respuestas token por token
- [ ] Persistir historial de conversación en disco/DB entre sesiones
- [ ] Agregar tests automatizados (`pytest`) para `calculate` y `run_tool`
- [ ] Soporte para múltiples tool calls en paralelo dentro de un mismo turno

---

**Parte de mi portfolio de proyectos aplicados a IA.** Ver los demás proyectos: [enlace a tu portfolio/repo principal]