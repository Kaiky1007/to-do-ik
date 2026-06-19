from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class TarefaBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    category: str = "Daily"
    divisoria_id: Optional[int] = None

class TarefaCreate(TarefaBase):
    pass

class TarefaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    divisoria_id: Optional[int] = None

class Tarefa(TarefaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DivisoriaBase(BaseModel):
    nome: str
    category: str

class DivisoriaCreate(DivisoriaBase):
    pass

class Divisoria(DivisoriaBase):
    id: int
    tarefas: List[Tarefa] = []
    
    model_config = ConfigDict(from_attributes=True)