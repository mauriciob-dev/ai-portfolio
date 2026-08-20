# AI Portfolio — Mauricio B.

Colección de proyectos aplicados de Inteligencia Artificial, construidos progresivamente para dominar el stack completo de un rol de AI Engineer / Backend con IA: desde integración de APIs de LLMs hasta sistemas RAG, agentes con herramientas, fine-tuning y despliegue en producción.

Cada proyecto vive en su propia carpeta, es independiente (su propio entorno virtual y dependencias), y tiene su propio README con el detalle técnico, decisiones de diseño y aprendizajes.

## Por qué este portfolio

Cada proyecto está diseñado para demostrar no solo que "funciona", sino **por qué funciona así** — decisiones de arquitectura, manejo de errores, y trade-offs explícitos. El objetivo es mostrar comprensión profunda del funcionamiento interno de sistemas con LLMs, no solo la capacidad de seguir un tutorial.

## Proyectos

| # | Proyecto | Descripción | Stack | Estado |
|---|---|---|---|---|
| 01 | [Chatbot con Function Calling](./01-call-api) | Chatbot conversacional que ejecuta herramientas reales (cálculo, hora) vía function calling, con memoria de contexto y manejo de errores en tres capas | Python, OpenAI API | ✅ Completo |
| 02 | RAG sobre documentos propios | Sistema de respuesta basado en recuperación semántica sobre PDFs/notas personales, usando embeddings y base vectorial | Python, OpenAI API, ChromaDB | 🔜 En progreso |
| 03 | Agente con herramientas y memoria | Agente que planifica múltiples pasos, usa varias herramientas y mantiene estado entre turnos | Python, LangGraph | ⏳ Pendiente |
| 04 | Fine-tuning / LoRA | Ajuste de un modelo open source para una tarea específica de clasificación o dominio | Python, Hugging Face, LoRA | ⏳ Pendiente |
| 05 | Proyecto end-to-end desplegado | Uno de los anteriores llevado a producción con tests, CI/CD y despliegue real | Docker, GitHub Actions, Render/Fly.io | ⏳ Pendiente |

## Cómo navegar este repo

Cada carpeta `0N-nombre-proyecto/` es autocontenida:

```
ai-portfolio/
├── 01-call-api/
│   ├── main.py
│   ├── README.md       # detalle técnico de este proyecto específico
│   ├── .env.example
│   └── .gitignore
├── 02-rag/
│   └── ...
└── README.md            # este archivo
```

Para correr cualquier proyecto, entra a su carpeta y sigue las instrucciones de setup en su README local — cada uno tiene su propio entorno virtual y variables de entorno.
