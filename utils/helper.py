
import re

def extract_json_from_markdown(text: str) -> str:
    """
    Extrai o JSON de um bloco markdown (```json ... ```) ou retorna o texto original se não houver bloco.
    """
    match = re.search(r"```json\s*([\[{].*[\]}])\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text