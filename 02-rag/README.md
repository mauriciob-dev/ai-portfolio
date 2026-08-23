# 📚 RAG sobre Documentos Propios (OpenAI + ChromaDB)

Sistema de preguntas y respuestas que responde basándose **exclusivamente** en el contenido de documentos PDF propios, usando el patrón RAG (Retrieval-Augmented Generation) para evitar que el modelo alucine información que no está en las fuentes.

## Por qué este proyecto

Los LLMs generan texto plausible incluso cuando no tienen la información correcta — responden con la misma confianza si aciertan o si inventan. RAG resuelve esto ancorando cada respuesta a fragmentos reales y verificables de documentos específicos, en lugar de depender del conocimiento general del modelo. Es uno de los patrones más solicitados hoy en roles de AI Engineer, porque es la base de asistentes internos, buscadores documentales y chatbots de soporte confiables.

## Cómo funciona

1. **Extracción**: cada PDF se lee con `pypdf`, extrayendo el texto página por página.
2. **Chunking**: el texto completo se divide en fragmentos de ~500 caracteres con 50 de solape (overlap), para no cortar ideas exactamente en el límite de un fragmento.
3. **Embeddings**: cada chunk se convierte en un vector numérico (`text-embedding-3-small` de OpenAI) que representa su significado en un espacio matemático — textos semánticamente similares quedan cerca entre sí.
4. **Almacenamiento**: los vectores se guardan en **ChromaDB** (base de datos vectorial local y persistente), junto con metadata que indica de qué documento vino cada chunk.
5. **Retrieval**: al hacer una pregunta, esta también se convierte en embedding, y se buscan los N chunks más cercanos por distancia vectorial (no por coincidencia de palabras clave).
6. **Generación anclada**: los chunks recuperados se inyectan como contexto explícito en el prompt, con la instrucción de responder *solo* con esa información y admitir explícitamente cuando no la tiene.

> El "anclaje" a los documentos no es un mecanismo técnico automático — es una instrucción en lenguaje natural dentro del prompt. El modelo puede, en teoría, ignorarla si el contexto es ambiguo o irrelevante; ver la sección de limitaciones.

## Prueba de valor: CON RAG vs. SIN RAG

Pregunta: *"¿En qué zonas se cultiva el cáñamo según el documento?"*

| | Respuesta |
|---|---|
| **Con RAG** | Cita datos exactos del documento: Francia como principal productor, seguido de Corea, China, Holanda y Polonia, con cifras de producción específicas. |
| **Sin RAG** | Menciona países reales (China, Francia) mezclados con datos no verificados (Alemania, EE.UU.) que no aparecen en el documento — sin forma de distinguir cuál es cuál. |

Esta comparación es la evidencia central de por qué RAG importa: sin él, un usuario no puede distinguir información real de información generada por conocimiento general del modelo.

## Limitación conocida (y por qué importa mencionarla)

El sistema actual siempre recupera los N chunks más cercanos, **sin filtrar por relevancia mínima**. Al probar con una pregunta totalmente ajena a los documentos ("¿cuál es la capital de Mongolia?"), ChromaDB igual devolvió 3 resultados — los "menos malos" de un lote irrelevante, con distancias muy superiores a las de búsquedas exitosas (>1.6 vs. ~0.6-0.8 en casos relevantes). El modelo logró identificar que el contexto no respondía la pregunta, pero eso dependió de su propia interpretación, no de un control explícito del sistema.

**Mejora pendiente:** descartar chunks cuya distancia supere un umbral (ej. 1.2) antes de construir el prompt, para que sea el sistema —no el modelo— quien decida cuándo no hay información suficiente.

## Stack

- Python 3.12
- [`openai`](https://github.com/openai/openai-python) — embeddings y generación
- [`chromadb`](https://www.trychroma.com/) — base de datos vectorial local
- [`pypdf`](https://pypdf.readthedocs.io/) — extracción de texto de PDFs
- [`python-dotenv`](https://github.com/theskumar/python-dotenv)

## Setup

```bash
cd 02-rag
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

python -m pip install chromadb pypdf openai python-dotenv

# Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY
```

Coloca tus PDFs en `data/`.

## Uso

```bash
# 1. Construir la base vectorial (una sola vez, o cuando cambien los documentos)
python -c "from main import build_database; build_database()"

# 2. Hacer preguntas
python main.py
```

```
=== CON RAG ===
Pregunta: ¿En qué siglo se popularizó el café en la península arábiga?
El café se popularizó en la península arábiga en el siglo XV...

=== SIN RAG ===
El café tiene una larga historia que se remonta a...
```

## Estructura del proyecto

```
02-rag/
├── main.py             # Extracción, chunking, embeddings, búsqueda y generación
├── data/                # PDFs fuente (no versionados si son privados)
├── chroma_db/            # Base vectorial persistente (generada, no versionar)
├── .env.example
└── README.md
```