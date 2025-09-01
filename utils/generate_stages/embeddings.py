from sentence_transformers import util
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config.settings import LOCAL_MODEL_PATH, INDEX_PATH, TOP_K

# Configura HuggingFaceEmbeddings para usar o modelo online
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
print("✅ Modelo HuggingFaceEmbeddings carregado!")

# Carrega o índice FAISS, com fallback se não encontrado
try:
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    print("✅ Índice FAISS carregado!")
except FileNotFoundError:
    print("⚠ Erro: Índice FAISS (forms_index/index.faiss) não encontrado. Rode index_forms.py primeiro!")
    exit(1)
except Exception as e:
    print(f"⚠ Erro ao carregar índice FAISS: {e}")
    exit(1)

def get_similar_forms(query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    top_docs = retriever.get_relevant_documents(query)
    top_forms = [doc.metadata for doc in top_docs]

    query_embedding = embeddings.embed_query(query)
    ranked_forms = []
    for doc in top_docs:
        form_description = doc.metadata.get("description", "")
        form_name = doc.metadata.get("name", "")
        description_segments = [s.strip() for s in form_description.split("\n") if s.strip()] if form_description else [""]
        form_text = f"{form_name} {' '.join(description_segments)}".strip()
        form_embedding = embeddings.embed_query(form_text)
        similarity = util.cos_sim(query_embedding, form_embedding)[0][0].item()
        ranked_forms.append((doc.metadata, similarity))

    ranked_forms = sorted(ranked_forms, key=lambda x: x[1], reverse=True)
    return [form[0] for form in ranked_forms[:TOP_K]], ranked_forms