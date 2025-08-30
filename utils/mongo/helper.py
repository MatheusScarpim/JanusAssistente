
from pymongo import MongoClient

def executar_query_mongodb(query: dict):
    client = MongoClient("mongodb://localhost:27017")
    db = client["janus"]  # nome do banco conforme seu prompt

    try:
        resultado = db.command(query)
        print(f"✅ Query executada com sucesso: {resultado}")
        return resultado
    except Exception as e:
        print(f"⚠ Erro ao executar a query no MongoDB: {e}")
        return {}
