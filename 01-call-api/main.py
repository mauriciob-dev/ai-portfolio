import os
import importlib
from dotenv import load_dotenv
import json
from datetime import datetime

from openai import APIError, APIConnectionError, RateLimitError

def calculate(expression: str) -> str:
    """Evalúa una expresión matemática simple."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def get_time() -> datetime:
    """Devuelve la hora y fecha actual."""
    try:
        return datetime.now()
    except Exception as e:
        return f"Error: {e}"
    
def run_tool(name, args):
    try:
        if name == "calculate":
            return calculate(args["expression"])
        if name == "get_time":
            return get_time()
        return f"Herramienta desconocida: {name}"
    except Exception as e:
        return f"Error ejecutando {name}: {e}"

OpenAI = importlib.import_module("openai").OpenAI

load_dotenv()

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evalúa una expresión matemática y devuelve el resultado",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "La expresión matemática a evaluar, ej: '15 * 7'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Devuelve la hora y fecha actual",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

messages = [
    {"role": "system", "content": "Para CUALQUIER operación matemática, sin importar cuán simple parezca, SIEMPRE debes usar la función calculate. Nunca calcules mentalmente."}
]
print("Chatbot listo. Escribe 'salir' para terminar.\n")

while True:
    user_input = input("Tú: ")
    if user_input.lower() == "salir":
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message
    messages.append(message)  # guardamos SIEMPRE la respuesta del assistant

    # ¿Pidió usar una tool?
    if message.tool_calls:
        for tool_call in message.tool_calls:
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}
                result = "Error: el modelo generó argumentos con formato inválido"
            else:
                result = run_tool(tool_call.function.name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
        except RateLimitError:
            print("Bot: Se agotaron los créditos o límite de rate. Intenta más tarde.")
            break
        except APIConnectionError:
            print("Bot: No hay conexión con OpenAI. Revisa tu internet.")
            continue
        except APIError as e:
            print(f"Bot: Error del API: {e}")
            continue
        message = response.choices[0].message
        messages.append(message)

    print("Bot:", message.content)