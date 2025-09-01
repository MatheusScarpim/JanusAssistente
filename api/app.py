import sys
import os
import json

# Ajuste de path (idealmente use pacote instalado, mas deixei como está)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import TOP_K

from flask import Flask, request, jsonify
from flask_cors import CORS

# --- IMPORTS: FIELDS ---
from utils.generate_fields.embeddings import (
    get_similar_forms as get_similar_forms_fields,
)
from utils.generate_fields.llm_helper import (
    generate_fields_prompt,
    process_fields_response,
)

# --- IMPORTS: STAGES ---
from utils.generate_stages.embeddings import (
    get_similar_forms as get_similar_forms_stages,
)
from utils.generate_stages.llm_helper import (
    generate_stages_prompt,
    process_stages_response,
)

# --- IMPORTS: ASSISTENT/MONGO ---
from utils.openai.helper import openai_request
from utils.mongo.helper import executar_query_mongodb
from utils.assistent.llm_helper import (generate_mongo_query, gerar_resposta_humanizada)

app = Flask(__name__)
CORS(app)


# ---------------------------
# Helpers
# ---------------------------
def bad_request(message: str):
    return jsonify({"status": "error", "message": message, "data": None}), 400


def internal_error(err: Exception):
    return (
        jsonify(
            {"status": "error", "message": f"Erro interno: {str(err)}", "data": None}
        ),
        500,
    )


def build_context(ranked_forms, top_k: int):
    """Normaliza o contexto do retorno para evitar KeyError."""
    if not ranked_forms:
        return []
    return [
        {
            "name": (form or {}).get("name", ""),
            "description": (form or {}).get("description", ""),
            "similarity": score,
        }
        for form, score in ranked_forms[: max(1, int(top_k or 0))]
    ]


# ---------------------------
# Rota: Geração de Campos
# ---------------------------
@app.route("/generate-form-fields", methods=["POST"])
def generate_form_fields():
    try:
        data = request.get_json(silent=True) or {}
        if "Context" not in data or "Quantity" not in data:
            return bad_request("Faltam parâmetros 'Context' ou 'Quantity' no corpo da requisição.")

        context = str(data["Context"]).strip()
        try:
            num_fields = int(data["Quantity"])
        except (ValueError, TypeError):
            return bad_request("'Quantity' deve ser um número inteiro positivo.")

        if not context or num_fields <= 0:
            return bad_request("O 'Context' não pode ser vazio e 'Quantity' deve ser positivo.")

        # Recupera similares (versão fields)
        top_forms, ranked_forms = get_similar_forms_fields(context)

        # Prompt + LLM (versão fields)
        prompt = generate_fields_prompt(context, num_fields, top_forms or [])
        response = openai_request(prompt)

        fields, error_message = process_fields_response(response, num_fields)

        response_data = {
            "status": "success" if not error_message else "warning",
            "message": error_message or "Campos gerados com sucesso.",
            "data": {
                "fields": fields,
                "context": build_context(ranked_forms, TOP_K),
            },
        }
        return jsonify(response_data), 200

    except Exception as e:
        return internal_error(e)


# ---------------------------
# Rota: Geração de Etapas
# ---------------------------
@app.route("/generate-form-stages", methods=["POST"])
def generate_form_stages():
    try:
        data = request.get_json(silent=True) or {}
        if "Context" not in data or "Quantity" not in data:
            return bad_request("Faltam parâmetros 'Context' ou 'Quantity' no corpo da requisição.")

        context = str(data["Context"]).strip()
        try:
            num_stages = int(data["Quantity"])
        except (ValueError, TypeError):
            return bad_request("'Quantity' deve ser um número inteiro positivo.")

        if not context or num_stages <= 0:
            return bad_request("O 'Context' não pode ser vazio e 'Quantity' deve ser positivo.")

        # Recupera similares (versão stages)
        top_forms, ranked_forms = get_similar_forms_stages(context)

        # Prompt + LLM (versão stages)
        prompt = generate_stages_prompt(context, num_stages, top_forms or [])
        response = openai_request(prompt)

        stages, error_message = process_stages_response(response, num_stages)

        response_data = {
            "status": "success" if not error_message else "warning",
            "message": error_message or "Etapas geradas com sucesso.",
            "data": {
                "stages": stages,
                "context": build_context(ranked_forms, TOP_K),
            },
        }
        return jsonify(response_data), 200

    except Exception as e:
        return internal_error(e)


# ---------------------------
# Rota: Assistente (Mongo)
# ---------------------------
@app.route("/assistent", methods=["POST"])
def massistent():
    try:
        data = request.get_json(silent=True) or {}
        if "pergunta" not in data:
            return bad_request("Faltou o parâmetro 'pergunta' no corpo da requisição.")

        pergunta = str(data["pergunta"]).strip()
        if not pergunta:
            return bad_request("'pergunta' não pode ser vazia.")

        mongo_query = generate_mongo_query(pergunta)
        resultado_query = executar_query_mongodb(mongo_query)

        # Se o executor já der uma resposta em texto (fallback/erro/explicação)
        if isinstance(resultado_query, str):
            return jsonify(
                {"status": "success", "data": {"resultado_humanizado": resultado_query}}
            ), 200

        # Serialização segura (ObjectId, datetime, etc.)
        mongo_query_serialized = json.loads(json.dumps(mongo_query, default=str))
        resultado_serialized = json.loads(json.dumps(resultado_query, default=str))

        resposta = gerar_resposta_humanizada(
            resultado_serialized, pergunta, mongo_query_serialized
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "query_mongodb": mongo_query_serialized,
                        "resultado": resultado_serialized,
                        "resposta_humanizada": resposta,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return internal_error(e)


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    # Use DEBUG via env var FLASK_DEBUG/FLASK_ENV em produção/testes
    app.run(host="0.0.0.0", port=5000, debug=True)
