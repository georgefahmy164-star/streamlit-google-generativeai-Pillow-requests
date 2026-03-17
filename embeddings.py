from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from PyPDF2 import PdfReader

embedder = SentenceTransformer("all-MiniLM-L6-v2")
documents = []
index = faiss.IndexFlatL2(384)

def add_to_knowledge(text):
    emb = embedder.encode([text])
    index.add(np.array(emb).astype("float32"))
    documents.append(text)

def search_knowledge(query):
    if len(documents) == 0:
        return ""
    emb = embedder.encode([query])
    D, I = index.search(np.array(emb).astype("float32"), k=3)
    results = [documents[i] for i in I[0] if i < len(documents)]
    return "\n".join(results)

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text
