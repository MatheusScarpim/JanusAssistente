import json
import os
from typing import Any, Dict, List
from langchain_ollama import OllamaLLM
import secrets
import re

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
llm = OllamaLLM(model=OLLAMA_MODEL)

HEX24_RE = re.compile(r"^[0-9a-f]{24}$")

def _new_id() -> str:
    # 24 hex chars
    return secrets.token_hex(12)

def _is_hex24(s: Any) -> bool:
    return isinstance(s, str) and bool(HEX24_RE.match(s))

def _to_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        vs = v.strip().lower()
        return vs in ("1", "true", "t", "yes", "y", "sim")
    return False

def generate_stages_prompt(name, num_stages, context):
    prompt_template = f"""
Com base nos processos semelhantes encontrados no dataset, incluindo nomes e descrições:

{json.dumps(context, ensure_ascii=False)}

Sugira EXATAMENTE {num_stages} estágios para criar um novo processo de "{name}".
Para cada estágio, forneça:
- "id": identificador único (24 chars hex).
- "taskReference": referência da tarefa.
- "type": tipo do estágio (sempre "task-user").
- "taskTitle": título da tarefa.
- "description": descrição do estágio.
- "isConcentrator": se o estágio é concentrador (boolean).
- "isNonTransferable": se o estágio é não-transferível (boolean).
- "isMobileAllowed": se permite acesso mobile (boolean).
- "notification": se terá notificação (boolean).
- "implementAprovation": se implementa aprovação (boolean).
- "communicationEmail": se envia comunicação por e-mail (boolean).
- "actions": lista de ações, cada uma com:
    - "labelButton": rótulo do botão.
    - "textHelp": texto de ajuda.
    - "position": posição (ordem) como string.
    - "stageDestinationId": id destino (24 hex) que deve referenciar um dos estágios do array.
    - "color": cor da ação/botão.
    - "icon": ícone da ação.

⚠ Retorne **somente** um array JSON válido com exatamente {num_stages} objetos, cada um com os campos acima. Não adicione texto explicativo, comentários ou qualquer outro conteúdo.

Exemplo para num_stages=2:
[
  {{
    "id": "5f8d0d55b54764421b7156c1",
    "taskReference": "Tarefa 1",
    "type": "task-user",
    "taskTitle": "Aprovação",
    "description": "Aprovar documento",
    "isConcentrator": true,
    "isNonTransferable": false,
    "isMobileAllowed": true,
    "notification": true,
    "implementAprovation": false,
    "communicationEmail": true,
    "actions": [
      {{
        "labelButton": "Aprovar",
        "textHelp": "Aprova o documento",
        "position": "1",
        "stageDestinationId": "5f8d0d55b54764421b7156c2",
        "color": "green",
        "icon": "check"
      }}
    ]
  }},
  {{
    "id": "5f8d0d55b54764421b7156c2",
    "taskReference": "Tarefa 2",
    "type": "task-user",
    "taskTitle": "Finalização",
    "description": "Concluir fluxo",
    "isConcentrator": false,
    "isNonTransferable": false,
    "isMobileAllowed": true,
    "notification": false,
    "implementAprovation": false,
    "communicationEmail": false,
    "actions": []
  }}
]
"""
    return prompt_template

def process_stages_response(response: str, num_stages: int):
    """
    Normaliza e valida a saída do LLM:
    - Garante lista com exatamente num_stages
    - IDs 24-hex únicos
    - Campos obrigatórios e tipos coerentes
    - 'type' = 'task-user'
    - 'position' string
    - 'stageDestinationId' 24-hex apontando para algum estágio (ajuste linear se faltar)
    """
    warnings: List[str] = []

    def _mk_stage_stub(i: int) -> Dict[str, Any]:
        return {
            "id": _new_id(),
            "taskReference": f"Tarefa {i}",
            "type": "task-user",
            "taskTitle": f"Título {i}",
            "description": f"Descrição {i}",
            "isConcentrator": False,
            "isNonTransferable": False,
            "isMobileAllowed": True,
            "notification": False,
            "implementAprovation": False,
            "communicationEmail": False,
            "actions": [],
        }

    try:
        if isinstance(response, str):
            raw = response.strip()
            print(f"process_stages_response raw response: {raw}")
            stages = json.loads(raw)
        else:
            print(f"process_stages_response response (not str): {response}")
            stages = response
        if not isinstance(stages, list):
            raise ValueError("Resposta não é um array JSON.")

        # 1) Truncar/Pad: exatamente num_stages
        if len(stages) > num_stages:
            stages = stages[:num_stages]
            warnings.append("Truncado para 'Quantity' solicitado.")
        elif len(stages) < num_stages:
            for i in range(len(stages) + 1, num_stages + 1):
                stages.append(_mk_stage_stub(i))
            warnings.append("Complementado com estágios extras para atingir 'Quantity'.")

        # 2) IDs 24-hex únicos
        used_ids = set()
        for i, s in enumerate(stages):
            sid = s.get("id")
            if not _is_hex24(sid) or sid in used_ids:
                new_id = _new_id()
                s["id"] = new_id
                warnings.append(f"ID inválido/duplicado no estágio {i+1}; gerado novo id.")
            used_ids.add(s["id"])

        # 3) Normalização de campos
        for s in stages:
            s["type"] = "task-user"  # força regra
            s["taskReference"] = str(s.get("taskReference", s.get("taskTitle", "")) or "").strip() or "Tarefa"
            s["taskTitle"] = str(s.get("taskTitle", s["taskReference"]) or "").strip() or "Tarefa"
            s["description"] = str(s.get("description", "") or "").strip()

            # Booleans
            s["isConcentrator"] = _to_bool(s.get("isConcentrator", False))
            s["isNonTransferable"] = _to_bool(s.get("isNonTransferable", False))
            s["isMobileAllowed"] = _to_bool(s.get("isMobileAllowed", True))
            s["notification"] = _to_bool(s.get("notification", False))
            s["implementAprovation"] = _to_bool(s.get("implementAprovation", False))
            s["communicationEmail"] = _to_bool(s.get("communicationEmail", False))

            # Actions
            actions = s.get("actions")
            if not isinstance(actions, list):
                actions = []
                warnings.append("Campo 'actions' ausente/ inválido; definido como lista vazia.")
            s["actions"] = actions
            for idx, a in enumerate(s["actions"]):
                a["labelButton"] = str(a.get("labelButton", f"Ação {idx+1}") or "")
                a["textHelp"] = str(a.get("textHelp", "") or "")
                a["position"] = str(a.get("position", str(idx + 1)))
                a["color"] = str(a.get("color", "") or "")
                a["icon"] = str(a.get("icon", "") or "")
                # stageDestinationId pode ser ajustado no passo 4

        # 4) Ajustar stageDestinationId (encadeamento linear quando faltar/for inválido)
        id_list = [s["id"] for s in stages]
        id_set = set(id_list)
        for i, s in enumerate(stages):
            last_idx = (i == len(stages) - 1)
            default_dest = id_list[i + 1] if not last_idx else id_list[i]  # último aponta para ele mesmo
            for a in s["actions"]:
                dest = a.get("stageDestinationId")
                if not _is_hex24(dest) or dest not in id_set:
                    a["stageDestinationId"] = default_dest

        warning_msg = "; ".join(warnings) if warnings else None
        return stages, warning_msg

    except Exception as e:
        print(f"process_stages_response exception: {e}")
        # Fallback simples
        stages = [_mk_stage_stub(i + 1) for i in range(num_stages)]
        # Colar fluxo linear em uma ação básica por estágio (exceto último)
        for i in range(num_stages):
            if i < num_stages - 1:
                stages[i]["actions"] = [{
                    "labelButton": "Próximo",
                    "textHelp": "Avança para o próximo estágio",
                    "position": "1",
                    "stageDestinationId": stages[i + 1]["id"],
                    "color": "primary",
                    "icon": "arrow-right"
                }]
        return stages, "O modelo não retornou JSON válido; gerados estágios fallback."
