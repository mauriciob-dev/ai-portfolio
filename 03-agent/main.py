import json
from ddgs import DDGS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def search_web(query: str) -> str:
    """Busca en internet y devuelve un resumen de los primeros resultados"""
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No se encontraron resultados."
        summary = "\n".join(f"- {r['title']}: {r['body']}" for r in results)
        return summary
    except Exception as e:
        return f"Error en la busqueda: {e}"

def calculate(expression: str) -> str:
    """Evalaua una expresion matematica simple"""
    try: 
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def save_note(content: str) -> str:
    """Guarda una nota de texto en un archivo local"""
    try:
        with open("notes.txt" ,"a", encoding="UTF-8") as f:
            f.write(content + "\n---\n")
        return "Nota guardada correctamente"
    except Exception as e:
        return f"Error guardando la nota: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Busca información actualizada en internet sobre cualquier tema, dato o evento reciente",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Los términos de búsqueda"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evalúa una expresión matemática y devuelve el resultado",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "La expresión matemática a evaluar"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Guarda una nota o resumen de texto en un archivo para referencia futura",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "El contenido de la nota a guardar"}
                },
                "required": ["content"]
            }
        }
    }
]

# Despachador: mapea nombre -> función real
def run_tool(name, args):
    try: 
        if name == "search_web":
            return search_web(args["query"])
        elif name == "calculate":
            return calculate(args["expression"])
        elif name == "save_note":
            return save_note(args["query"])
        return f"Herramienta desconocida: {name}"
    except Exception as e:
        return f"Error ejecutando {name}: {e}"
    
def run_agent(user_message: str, max_iterations: int = 5):
    messages = [
        {"role": "system", "content": "Eres un asistente que puede buscar información en internet, hacer cálculos y guardar notas. Usa las herramientas que necesites, en el orden que necesites, hasta tener toda la información para responder completamente."},
        {"role": "user", "content": user_message}
    ]

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            print(f" [Paso {iteration+1}] {tool_call.function.name}({args})")
            result = run_tool(tool_call.function.name, args)
            print(f" [Resultado] {result[:150]}...")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    return "Se alcanzó el límite de iteraciones sin llegar a una respuesta final."

def run_simple_chatbot(user_message: str):
    messages = [
        {"role": "system", "content": "Eres un asistente que puede buscar información en internet y hacer cálculos."},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    message = response.choices[0].message
    messages.append(message)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            print(f"  [Única ronda] {tool_call.function.name}({args})")
            result = run_tool(tool_call.function.name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        return final.choices[0].message.content

    return message.content

if __name__ == "__main__":
    query = "Busca el precio actual del dólar en Colombia y calcula cuánto son 500 USD en pesos colombianos"

    print("=== CHATBOT SIMPLE (1 sola tool call) ===")
    print(run_simple_chatbot(query))

    print("\n=== AGENTE (multi-paso) ===")
    print(run_agent(query))