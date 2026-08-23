import chromadb
from pypdf import PdfReader
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def build_database():
    chrome_client = chromadb.PersistentClient(path='./chroma_db')
    collection = chrome_client.get_or_create_collection(name="documentos")

    docs = {
        "cafe": "data/cafe.pdf",
        "fotosintesis": "data/fotosintesis.pdf",
        "sativa": "data/sativa.pdf"
    }

    for doc_name, path in docs.items():
        text = extract_text(path)
        chunks = chunk_text(text)

        for i , chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            collection.add(
                ids=[f"{doc_name}_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": doc_name}]
            )
        print(f"{doc_name}: {len(chunks)} chunks generados")
    return collection

def search(query: str, n_results: int = 3):
    chroma_client = chromadb.PersistentClient("./chroma_db")
    collection = chroma_client.get_or_create_collection(name="documentos")

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    print(f"\nPregunta: {query}")
    print(f"Chunks recuperados: {len(results['documents'][0])}\n")
    
    UMBRAL = 1.2

    filtered = []
    
    for i , (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"--- Resultado {i+1} (fuente: {meta['source']}, distancia: {dist:.4f})")
        print(doc[:200])
        print()
        if dist <= UMBRAL:
            filtered.append((doc, meta, dist))

    return filtered

def ask_with_rag(query: str) -> str:
    results = search(query, n_results=3)
    context = "\n\n".join([doc for doc in results])

    prompt = f"""Responde la pregunta SOLO usando la informacion del siguiente contexto.
Si el contexto no contiene la respuesta, di explicitamente que no tienes esa informacion.

Contexto: {context}

Pregunta: {query}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def ask_without_rag(query: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content
    
if __name__ == "__main__":
    query = "¿En qué zonas se cultiva el cáñamo según el documento?"

    print("=== CON RAG ===")
    print(ask_with_rag(query))

    print("\n=== SIN RAG ===")
    print(ask_without_rag(query))
