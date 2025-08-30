import json
import requests
import os

from utils.helper import extract_json_from_markdown

def openai_request(prompt: str, model: str = "gpt-4", temperature: float = 0.7) -> str:
	"""
	Faz uma requisição para a API da OpenAI e retorna a resposta do modelo.
	"""

	url = "https://api.openai.com/v1/chat/completions"
	headers = {
		"Authorization": f"Bearer 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",
		"Content-Type": "application/json"
	}
	data = {
		"model": model,
		"messages": [
			{"role": "user", "content": prompt}
		],
		"temperature": temperature
	}
	response = requests.post(url, headers=headers, json=data)
	response.raise_for_status()
	result = response.json()
	json_text = extract_json_from_markdown(result["choices"][0]["message"]["content"])
	print(json_text)
	try:
		return json.loads(json_text)
	except json.JSONDecodeError:
		return json_text



