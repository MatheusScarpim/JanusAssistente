import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# 1️⃣ Carrega o dataset
try:
    with open("forms_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    if not dataset:
        raise ValueError("Dataset está vazio!")
except FileNotFoundError:
    print("⚠ Erro: forms_dataset.json não encontrado em C:\\Users\\mathe\\OneDrive\\DD\\GitHub\\JanusIa")
    exit(1)
except json.JSONDecodeError:
    print("⚠ Erro: forms_dataset.json tem formato inválido")
    exit(1)

# 2️⃣ Preprocessa documentos para focar em name e description
docs = []
for form in dataset:
    text = f"{form.get('name', '')} {form.get('description', '')}".strip()
    if text:
        docs.append(Document(page_content=text, metadata=form))

# 3️⃣ Cria embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 4️⃣ Cria o índice FAISS
try:
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local("forms_index")
    print("✅ Índice FAISS criado e salvo em forms_index!")
except Exception as e:
    print(f"⚠ Erro ao criar índice FAISS: {e}")
    exit(1)