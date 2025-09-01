
import json
from models.assistent import SCHEMA
from models.field import create_field, normalize_type
import os

# from langchain_ollama import OllamaLLM

# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
# llm = OllamaLLM(model=OLLAMA_MODEL)

def generate_fields_prompt(name, num_fields, context):
    prompt_template = f"""
Com base nos formulários semelhantes encontrados no dataset, incluindo nomes e descrições:

{json.dumps(context, ensure_ascii=False)}

Sugira EXATAMENTE {num_fields} campos para criar um novo formulário de "{name}".
Para cada campo, forneça:
- "identifier": um identificador único e relevante.
- "type": o tipo de campo mais adequado entre: LineText, TextArea, Number, Select, Checkbox, Radio, Toggle, Date.
- "label": um rótulo descritivo para o campo.
- "options": uma lista de opções (com "text" e "value") para campos Select ou Radio; omita para outros tipos.

⚠ Retorne **somente** um array JSON válido com exatamente {num_fields} objetos, cada um com "identifier", "type", "label" e, se aplicável, "options". 
Não adicione texto explicativo, comentários ou qualquer outro conteúdo.

Exemplo para num_fields=3:
[{{"identifier": "nome", "type": "LineText", "label": "Nome Completo"}}, {{"identifier": "CPF", "type": "LineText", "label": "CPF"}}, {{"identifier": "tipo_pessoa", "type": "Select", "label": "Tipo de Pessoa", "options": [{{"text": "Física", "value": "fisica"}}, {{"text": "Jurídica", "value": "juridica"}}]}}]
"""
    return prompt_template

def process_fields_response(response, num_fields):
    try:
        fields_data = json.loads(response.strip())
        seen = set()
        unique_fields = []
        for f in fields_data:
            if f["identifier"] not in seen:
                f["type"] = normalize_type(f["type"])
                unique_fields.append(f)
                seen.add(f["identifier"])
        fields_data = unique_fields

        if len(fields_data) > num_fields:
            fields_data = fields_data[:num_fields]
        elif len(fields_data) < num_fields:
            for i in range(num_fields - len(fields_data)):
                fields_data.append({
                    "identifier": f"campo_extra_{i+1}",
                    "type": "LineText",
                    "label": f"Campo Extra {i+1}"
                })

        fields = [create_field(
            f["identifier"],
            f["type"],
            i + 1,
            f.get("label", f["identifier"].capitalize()),
            f.get("options")
        ) for i, f in enumerate(fields_data)]
        return fields, None
    except json.JSONDecodeError:
        fallback_fields = [
            {"identifier": "nome", "type": "LineText", "label": "Nome Completo"},
            {"identifier": "CPF", "type": "LineText", "label": "CPF"}
        ]
        fields_data = fallback_fields[:num_fields]
        if len(fields_data) < num_fields:
            for i in range(num_fields - len(fields_data)):
                fields_data.append({
                    "identifier": f"campo_extra_{i+1}",
                    "type": "LineText",
                    "label": f"Campo Extra {i+1}"
                })
        fields = [create_field(
            f["identifier"],
            f["type"],
            i + 1,
            f.get("label", f["identifier"].capitalize()),
            f.get("options")
        ) for i, f in enumerate(fields_data)]
        return fields, "O modelo não retornou JSON válido, usado fallback."
    