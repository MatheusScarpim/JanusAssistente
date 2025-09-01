from typing import List, Optional
from pydantic import BaseModel, Field

class Action(BaseModel):
    labelButton: str = Field(..., description="Rótulo do botão")
    textHelp: str = Field(..., description="Texto de ajuda")
    position: str = Field(..., description="Posição (ordem) como string")
    stageDestinationId: str = Field(..., description="BsonId destino (24 hex)")
    color: str = Field(..., description="Cor da ação/botão")
    icon: str = Field(..., description="Ícone da ação")

class Stage(BaseModel):
    id: str = Field(..., description="BsonId (24 chars hex)")
    taskReference: str = Field(..., description="Referência da tarefa")
    type: str = Field(..., description="Tipo do estágio (sempre task-user)")
    taskTitle: str = Field(..., description="Título da tarefa")
    description: str = Field(..., description="Descrição do estágio")
    isConcentrator: bool = Field(..., description="Se o estágio é concentrador")
    isNonTransferable: bool = Field(..., description="Se o estágio é não-transferível")
    isMobileAllowed: bool = Field(..., description="Se permite acesso mobile")
    notification: bool = Field(..., description="Se terá notificação")
    implementAprovation: bool = Field(..., description="Se implementa aprovação")
    communicationEmail: bool = Field(..., description="Se envia comunicação por e-mail")
    actions: List[Action]

class StageResponse(BaseModel):
    stages: List[Stage]