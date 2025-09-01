import json
from langchain_community.llms import Ollama
from typing import Dict, Any

from models.assistent import EXAMPLES, SCHEMA
from utils.helper import extract_json_from_markdown
from utils.openai.helper import openai_request

def create_prompt_assistent(query: str) -> str:
    return f"""
Você é um especialista em MongoDB e deve gerar uma query MongoDB (em formato de aggregation pipeline ou find) para a pergunta fornecida, com base no esquema e exemplos abaixo. A query deve ser válida, seguir a sintaxe do MongoDB e ser otimizada para a pergunta.

**Pergunta do usuário**: {query}    

**Esquema do banco de dados**:
```json
{json.dumps(SCHEMA, indent=2, ensure_ascii=False)}
```

**Exemplos de documentos**:
```json
{json.dumps(EXAMPLES, indent=2, ensure_ascii=False)}
```

**Instruções**:
1. Gere uma query MongoDB que responda à pergunta do usuário.
2. Use `$match`, `$lookup`, `$unwind`, etc., quando necessário para combinar dados entre as coleções `form` e `process``   .
3. Para contar elementos em arrays (ex.: `fields`), use o operador `$size` para maior eficiência, especialmente quando o array pode estar vazio.
4. Retorne apenas a query MongoDB em formato JSON, sem explicações adicionais.
5. Certifique-se de que a query é válida e respeita o esquema fornecido.
6. Sempre que for comparar ou buscar pelo campo _id, converta o valor para ObjectId usando $toObjectId ou ObjectId() conforme o contexto, por exemplo: $toObjectId: $formId. O campo formId em process e o campo _id em form são ambos ObjectId, então a comparação correta é entre $_id e $formId convertido para ObjectId.
7. Para buscas em arrays (ex.: `fields`), use `$size` para contagem ou `$elemMatch` para filtros específicos.
8. Lide com casos em que arrays como `fields` podem estar vazios, retornando 0 quando apropriado.
9. Apenas o JSON, sem explicações.
10. Para evitar "a group specification must include an _id" adicione _id: null nas coisas que precisam
11. Vai ser sempre executado no db.runCommand não pode faltar o cursos
12. Ele vai ser um runCommand então preciso da declaração de todas as tabelas
13. Sempre inclua o campo "cursor":  no objeto JSON retornado para comandos de agregação.
14. Nem sempre é necessário gerar uma query MongoDB. Então de uma resposta com se fosse um assistente virtual.
15. Se a pergunta do usuário não requer uma consulta ao banco de dados, forneça uma resposta direta com base no conhecimento prévio.
16. Todos _id são objectId não esqueça
17. Sempre que for comparar ou buscar nomes (strings), labels (strings) e tudo que tenha texto, utilize operadores que ignorem maiúsculas/minúsculas, como $toLower ou $regex com opção 'i' para garantir que a busca seja insensível a maiúsculas/minúsculas.
18  . sempre usar esse pipeline correto para relacionar e process.formId (string) com form._id (ObjectId):
"""
{
    "$lookup": {
        "from": "form",
        "let": { "formIdObj": { "$toObjectId": "$formId" } },
        "pipeline": [
            { "$match": { "$expr": { "$eq": [ "$_id", "$$formIdObj" ] } } }
        ],
        "as": "form"
    }
}
"""
19. Por favor quando for a query retorne só o json

**Saída esperada**:
Apenas um objeto JSON contendo a query MongoDB ou um pipeline completo).
"""


def call_ollama(prompt: str) -> Dict[str, Any]:
    try:
        llm = Ollama(model="gpt-oss")
        response = llm(prompt)
        json_text = extract_json_from_markdown(response)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            print(f"⚠ Resposta do Ollama não é um JSON válido: {response}")
            return {}
    except Exception as e:
        print(f"⚠ Erro ao chamar o Ollama: {e}")
        return {}


def generate_mongo_query(query: str) -> Dict[str, Any]:
    try:
        prompt = create_prompt_assistent(query)
        # query_json = call_ollama(prompt)
        query_json = openai_request(prompt)
        return query_json
    except Exception as e:
        print(f"⚠ Erro ao gerar a query: {e}")
        return {}

def gerar_resposta_humanizada(resultado: dict, pergunta: str, query: str) -> str:
    # llm_leve = Ollama(model="gemma3:4b")
    prompt = (
        f"Pergunta do usuário: {pergunta}\n"
        f"Resultado da consulta: {json.dumps(resultado, ensure_ascii=False, default=str)}\n\n"
        "Responda apenas o que foi pedido pelo usuário, de forma direta e objetiva, sem exemplos, explicações ou frases extras. Não use termos técnicos, não mencione banco de dados. Apenas a resposta final. Em portugues brasil."
    )
    resposta = openai_request(prompt)
    return resposta