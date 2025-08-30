
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import TOP_K

from flask import Flask, request, jsonify
from utils.generate_fields.embeddings import get_similar_forms
from utils.generate_fields.llm_helper import generate_fields_prompt, process_fields_response, llm
from utils.mongo.helper import executar_query_mongodb
from utils.openai.helper import openai_request

from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

@app.route('/generate-form-fields', methods=['POST'])
def generate_form_fields():
    try:
        data = request.get_json()
        if not data or 'Context' not in data or 'Quantity' not in data:
            return jsonify({
                "status": "error",
                "message": "Faltam parâmetros 'Context' ou 'Quantity' no corpo da requisição.",
                "data": None
            }), 400

        name = data['Context']
        num_fields = int(data['Quantity'])

        if not name.strip() or num_fields <= 0:
            return jsonify({
                "status": "error",
                "message": "O nome não pode ser vazio e num_fields deve ser positivo.",
                "data": None
            }), 400

        top_forms, ranked_forms = get_similar_forms(name)

        prompt = generate_fields_prompt(name, num_fields, top_forms)
        response = llm.invoke(prompt)
        fields, error_message = process_fields_response(response, num_fields)

        response_data = {
            "status": "success" if not error_message else "warning",
            "message": error_message or "Campos gerados com sucesso.",
            "data": {
                "fields": fields,
                "context": [
                    {
                        "name": form.get('name', ''),
                        "description": form.get('description', ''),
                        "similarity": score
                    } for form, score in ranked_forms[:TOP_K]
                ]
            }
        }
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro interno: {str(e)}",
            "data": None
        }), 500
    
from utils.assistent.llm_helper import generate_mongo_query, gerar_resposta_humanizada

@app.route('/assistent', methods=['POST'])
def massistent():
    try:
        data = request.get_json()
        if not data or 'pergunta' not in data:
            return jsonify({
                "status": "error",
                "message": "Faltou o parâmetro 'pergunta' no corpo da requisição.",
                "data": None
            }), 400

        pergunta = data['pergunta']
        mongo_query = generate_mongo_query(pergunta)
        resultadoQuery = executar_query_mongodb(mongo_query)

        # Se resultadoQuery for texto, retorna só o texto
        if isinstance(resultadoQuery, str):
            return jsonify({
                "status": "success",
                "data": {
                    "resultado_humanizado": resultadoQuery
                }
            }), 200

        # Serializa para garantir que ObjectId não cause erro
        mongo_query_serialized = json.loads(json.dumps(mongo_query, default=str))
        resultado_serialized = json.loads(json.dumps(resultadoQuery, default=str))

        resposta = gerar_resposta_humanizada(resultado_serialized, pergunta, mongo_query_serialized)

        return jsonify({
            "status": "success",
            "data": {
                "query_mongodb": mongo_query_serialized,
                "resultado": resultado_serialized,
                "resposta_humanizada": resposta
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro interno: {str(e)}",
            "data": None
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)