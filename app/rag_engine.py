from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.embeddings.base import Embeddings
from groq import Groq
import os
import shutil
import hashlib
import random
from dotenv import load_dotenv

load_dotenv()

# ── Global trackers ──────────────────────────────────────────────
_chroma_client = None
_current_db_path = None

# ── Embeddings ───────────────────────────────────────────────────
class GroqEmbeddings(Embeddings):
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def embed_documents(self, texts):
        return [self._embed(t) for t in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        random.seed(hash_val)
        return [random.uniform(-1, 1) for _ in range(384)]

# ── Clear vector store ───────────────────────────────────────────
def clear_vector_store():
    global _chroma_client, _current_db_path

    if _chroma_client is not None:
        try:
            _chroma_client._client._system.stop()
        except Exception:
            pass
        try:
            _chroma_client._client.close()
        except Exception:
            pass
        _chroma_client = None

    if _current_db_path and os.path.exists(_current_db_path):
        try:
            shutil.rmtree(_current_db_path)
            print("🗑️ Old vector store cleared!")
        except Exception as e:
            print(f"⚠️ Could not delete old DB: {e}")

    _current_db_path = None

# ── Build RAG ────────────────────────────────────────────────────
def build_rag(transcript: str):
    global _chroma_client, _current_db_path

    clear_vector_store()

    print("✂️ Splitting transcript into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.create_documents([transcript])
    print(f"✅ Created {len(chunks)} chunks")

    print("🔍 Building fresh vector store...")
    embeddings = GroqEmbeddings()

    # Unique database every upload
    _current_db_path = f"./chroma_db_{random.randint(1000, 999999)}"

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=_current_db_path
    )

    _chroma_client = vectorstore
    print("✅ Fresh vector store ready!")

    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 5}
        ),
        return_source_documents=False
    )

    return qa_chain

# ── Ask question ─────────────────────────────────────────────────
def ask_question(qa_chain, question: str) -> str:
    strict_query = f"""
You must answer ONLY from the provided transcript context.

Rules:
1. Do NOT invent names, events, places, or actions.
2. Do NOT use outside knowledge.
3. If the answer is not clearly present in the transcript, say:
   "This is not mentioned in the current video transcript."
4. Keep answers accurate and concise.

Question: {question}
"""
    result = qa_chain.invoke({"query": strict_query})
    return result["result"]
