SCHEMA = {
    "form": {
        "description": "Coleção que armazena formulários com seus campos e metadados.",
        "fields": {
            "_id": {"type": "ObjectId", "description": "Identificador único do formulário"},
            "name": {"type": "string", "description": "Nome do formulário"},
            "description": {"type": "string", "description": "Descrição do formulário"},
            "createdAt": {"type": "Date", "description": "Data de criação"},
            "updatedAt": {"type": "Date", "description": "Data de última atualização"},
            "status": {"type": "string", "description": "Status do formulário (ex.: Active, Inactive)"},
            "sections": {"type": "array<string>", "description": "Lista de seções (opcional)", "nullable": True},
            "manager": {"type": "string", "description": "Gerente responsável"},
            "version": {"type": "int", "description": "Versão do formulário"},
            "branchs": {"type": "array<string>", "description": "Lista de filiais aqui esta com string mas é um objectId (opcional)", "nullable": True},
            "hasPriority": {"type": "boolean", "description": "Indica se o formulário tem prioridade"},
            "stages": {"type": "array<object>", "description": "Lista de estágios do formulário"},
            "fields": {
                "type": "array<object>",
                "description": "Lista de campos do formulário, pode ser vazio",
                "subfields": {
                    "position": {"type": "int", "description": "Posição do campo"},
                    "identifier": {"type": "string", "description": "Identificador único do campo"},
                    "label": {"type": "string", "description": "Rótulo do campo"},
                    "type": {"type": "string", "description": "Tipo do campo (ex.: text, email)"},
                    "required": {"type": "boolean", "description": "Indica se o campo é obrigatório"},
                    "disabled": {"type": "boolean", "description": "Indica se o campo está desativado"},
                    "protected": {"type": "boolean", "description": "Indica se o campo é protegido"},
                    "placeholder": {"type": "string", "description": "Placeholder do campo"},
                    "visible": {"type": "boolean", "description": "Indica se o campo é visível"},
                    "defaultValue": {"type": "string", "description": "Valor padrão (opcional)", "nullable": True},
                    "options": {"type": "array<object>", "description": "Opções para campos de seleção (opcional)", "nullable": True},
                    "description": {"type": "string", "description": "Descrição do campo (opcional)", "nullable": True},
                    "group": {"type": "object", "description": "Grupo ao qual o campo pertence"},
                    "conditions": {"type": "object", "description": "Condições do campo (opcional)", "nullable": True},
                    "size": {"type": "object", "description": "Tamanho do campo"},
                    "createdAt": {"type": "Date", "description": "Data de criação do campo"},
                    "updatedAt": {"type": "Date", "description": "Data de atualização do campo"},
                    "helpText": {"type": "string", "description": "Texto de ajuda (opcional)", "nullable": True},
                    "suspended": {"type": "boolean", "description": "Indica se o campo está suspenso (opcional)", "nullable": True}
                }
            },
            "permissions": {"type": "object", "description": "Permissões do formulário (opcional)", "nullable": True},
            "script": {"type": "object", "description": "Script associado ao formulário (opcional)", "nullable": True}
        }
    },
    "process": {
        "description": "Coleção que armazena processos associados a formulários.",
        "fields": {
            "_id": {"type": "ObjectId", "description": "Identificador único do processo"},
            "protocol": {"type": "string", "description": "Protocolo do processo (opcional)", "nullable": True},
            "formId": {"type": "string", "description": "ID do formulário associado"},
            "cycle": {"type": "int", "description": "Ciclo do processo"},
            "executors": {"type": "array<string>", "description": "Lista de executores (opcional)", "nullable": True},
            "stageId": {"type": "string", "description": "ID do estágio atual (opcional)", "nullable": True},
            "createdAt": {"type": "Date", "description": "Data de criação (opcional)", "nullable": True},
            "status": {"type": "int", "description": "Status do processo tem que ser numero para comparar corretamente (ex.: 0 em andamento)"},
            "stages": {
                "type": "array<object>",
                "description": "Lista de estágios do processo",
                "subfields": {
                    "_id": {"type": "ObjectId", "description": "Identificador único do estágio (opcional)", "nullable": True},
                    "processId": {"type": "string", "description": "ID do processo"},
                    "stageId": {"type": "string", "description": "ID do estágio"},
                    "labelButton": {"type": "string", "description": "Texto do botão do estágio (opcional)", "nullable": True},
                    "cycle": {"type": "int", "description": "Ciclo do estágio"},
                    "executor": {"type": "string", "description": "Executor do estágio (opcional)", "nullable": True},
                    "status": {"type": "int", "description": "Status do estágio"}
                }
            },
            "openBy": {"type": "string", "description": "Usuário que abriu o processo"}
        }
    },
    "branch" : {
        "_id": {"type": "ObjectId", "description": "Identificador único do branch"},
        "name": {"type": "string", "description": "Nome do branch"}
    },
    "sector": {
        "_id": {"type": "ObjectId", "description": "Identificador único do setor"},
        "name": {"type": "string", "description": "Nome do setor"}
    }

}

# Exemplos de documentos
EXAMPLES = [
    {
        "_id": "68a5bebebe3b6c5719e1b128 é um objectId",
        "name": "Gestão de RH",
        "description": "",
        "createdAt": "2025-08-20T12莎25:19.160Z",
        "updatedAt": "2025-08-20T12:25:56.938Z",
        "status": 0,
        "sections": [],
        "manager": "",
        "version": 1,
        "branchs": ["68a5becabe3b6c5719e1b129"],
        "hasPriority": False,
        "stages": [],
        "fields": [],
    },
    {
        "_id": "456 é um objectId",
        "protocol": "PROC-001",
        "formId": "68a5bebebe3b6c5719e1b128",
        "status": 0,
        "createdAt": "2025-08-22T14:00:00Z",
        "openBy": "Maria",
        "branchs": ["68a5becabe3b6c5719e1b129 é um object id"],
        "cycle": 1,
        "stages": [
            {
                "processId": "456",
                "stageId": "stage1",
                "labelButton": "Enviar",
                "executor": "Maria",
                "status": "0",
                "cycle": 1
            }
        ]
    }
]
