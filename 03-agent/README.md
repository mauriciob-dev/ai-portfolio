# 🕵️ Agente con Herramientas y Memoria (Multi-Step Reasoning)

Agente que encadena múltiples llamadas a herramientas en una misma tarea, decidiendo dinámicamente cuántos pasos necesita antes de responder — a diferencia de un chatbot con function calling simple, que solo tiene una ronda de ida y vuelta.

## Por qué este proyecto

Muchas tareas reales requieren que el resultado de una acción alimente la siguiente: buscar un dato antes de poder calcular algo con él, por ejemplo. Un sistema de function calling simple (una sola ronda) no puede resolver esas dependencias — no tiene oportunidad de "ver" el resultado de una tool y decidir, con esa información nueva, que necesita otra más. Este proyecto demuestra la diferencia con evidencia directa: la misma tarea falla en un patrón y se resuelve completa en el otro.

## Cómo funciona

1. El agente recibe una tarea del usuario y entra a un **loop de razonamiento** (máximo N iteraciones, protección contra loops infinitos).
2. En cada iteración, llama al modelo con el historial completo y la lista de tools disponibles.
3. Si el modelo **no** pide ninguna tool, se asume que ya tiene toda la información necesaria y su respuesta de texto es la final — el loop termina.
4. Si el modelo pide una o más tools, el código las ejecuta **todas** (el API exige una respuesta por cada `tool_call_id` solicitado en la misma ronda), agrega los resultados al historial, y vuelve a preguntarle al modelo en la siguiente iteración — **ahora con el resultado ya visible**.
5. Este ciclo se repite hasta que el modelo decide que ya puede responder, o hasta alcanzar el límite de iteraciones (protección ante bugs o loops que nunca terminan).

## Herramientas (tools) implementadas

| Tool         | Descripción                                     | Fuente                                  |
| ------------ | ----------------------------------------------- | --------------------------------------- |
| `search_web` | Busca información actualizada en internet       | `ddgs` (DuckDuckGo Search, sin API key) |
| `calculate`  | Evalúa una expresión matemática de forma segura | Local                                   |
| `save_note`  | Guarda una nota de texto en un archivo local    | Local                                   |

## Prueba de valor: agente multi-paso vs. chatbot de una sola ronda

Tarea: _"Busca el precio actual del dólar en Colombia y calcula cuánto son 500 USD en pesos colombianos"_ — una tarea con dependencia explícita entre pasos (el cálculo necesita el resultado de la búsqueda).

|                              | Comportamiento                                                                                                       | Resultado                                                                     |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Chatbot simple** (1 ronda) | Pide `search_web`, obtiene el precio, pero no tiene una segunda ronda disponible para pedir `calculate` con ese dato | **Falla — responde `None`, sin texto ni tool call**                           |
| **Agente** (multi-paso)      | Pide `search_web`, ve el resultado, y en la siguiente iteración pide `calculate` con la cifra extraída               | **Resuelve correctamente: "500 USD equivalen a 1,528,255 pesos colombianos"** |

Esta no es una diferencia de calidad de respuesta — es una **falla total contra una tarea completada**, y es la evidencia central de cuándo el patrón de agente aporta valor real sobre function calling simple: específicamente, cuando existe dependencia entre los datos de distintos pasos.

## Decisiones de diseño relevantes

- **Límite de iteraciones (`max_iterations=5`)**: sin este límite, un bug o una tool que falla repetidamente podría generar un loop indefinido de llamadas a la API — costoso y peligroso en producción. Se verificó explícitamente bajando el límite a 1 con una tarea que requiere 2 pasos, confirmando que el sistema corta el loop con un mensaje controlado en vez de fallar silenciosamente.
- **Ejecutar todas las tool calls de una ronda antes de responder**: el API exige que cada `tool_call_id` solicitado en un mensaje del assistant tenga su respuesta correspondiente — omitir alguna produce un error 400 explícito, no un fallo silencioso.
- **Elección de cifra ambigua**: en búsquedas reales, los resultados de `search_web` a menudo contienen múltiples cifras distintas (por fuentes o fechas diferentes) sin una única "verdad". El modelo elige una sin que el sistema valide cuál — un punto ciego real de este diseño que vale la pena auditar en un caso de uso serio.

## Stack

- Python 3.12
- [`openai`](https://github.com/openai/openai-python)
- [`ddgs`](https://pypi.org/project/ddgs/) — búsqueda web sin API key
- [`python-dotenv`](https://github.com/theskumar/python-dotenv)

## Setup

```bash
cd 03-agent
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

python -m pip install openai ddgs python-dotenv

cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY
```

## Uso

```bash
python main.py
```

```
[Paso 1] search_web({'query': 'precio actual del dólar en Colombia'})
[Paso 2] calculate({'expression': '500 * 3056.51'})

Respuesta final: El precio actual del dólar en Colombia es de aproximadamente
3,056.51 pesos colombianos. Por lo tanto, 500 USD equivalen a 1,528,255 pesos colombianos.
```

## Estructura del proyecto

```
03-agent/
├── main.py             # Definición de tools, loop del agente, chatbot simple (comparación)
├── notes.txt             # Generado por save_note (no versionar si tiene datos de prueba)
├── .env.example
└── README.md
```
