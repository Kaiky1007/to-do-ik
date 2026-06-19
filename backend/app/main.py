from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

from .database import engine, Base, get_db
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="To-Do Widget API")

@app.get("/")
def ler_raiz():
    return {"mensagem": "API do To-Do Widget está online! Acesse /docs para testar."}

@app.post("/tarefas/", response_model=schemas.Tarefa, status_code=status.HTTP_201_CREATED)
def criar_tarefa(tarefa: schemas.TarefaCreate, db: Session = Depends(get_db)):
    db_tarefa = models.Tarefa(
        title=tarefa.title,
        description=tarefa.description,
        is_completed=tarefa.is_completed,
        category=tarefa.category,
        divisoria_id=tarefa.divisoria_id
    )
    db.add(db_tarefa)
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


@app.get("/tarefas/", response_model=List[schemas.Tarefa])
def listar_tarefas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hoje = date.today()
    ultimo_domingo = get_ultimo_domingo(hoje)
    tarefas = db.query(models.Tarefa).all()
    houve_alteracao = False
    for t in tarefas:
        if t.category == "Daily":
            if t.last_reset < hoje:
                t.is_completed = False
                t.last_reset = hoje
                houve_alteracao = True
        elif t.category == "Weekly":
            if t.last_reset < ultimo_domingo:
                t.is_completed = False
                t.last_reset = hoje
                houve_alteracao = True
    if houve_alteracao:
        db.commit()
    return db.query(models.Tarefa).offset(skip).limit(limit).all()


@app.get("/tarefas/{tarefa_id}", response_model=schemas.Tarefa)
def obter_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    db_tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return db_tarefa


@app.put("/tarefas/{tarefa_id}", response_model=schemas.Tarefa)
def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: schemas.TarefaUpdate, db: Session = Depends(get_db)):
    db_tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    # Atualiza apenas os campos enviados na requisição
    dados_atualizacao = tarefa_atualizada.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizacao.items():
        setattr(db_tarefa, campo, valor)
        
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


@app.delete("/tarefas/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    db_tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    db.delete(db_tarefa)
    db.commit()
    return None

def get_ultimo_domingo(hoje: date):
    # weekday() no Python: Segunda é 0, Domingo é 6.
    dias_para_domingo = (hoje.weekday() + 1) % 7
    return hoje - timedelta(days=dias_para_domingo)

@app.post("/tarefas/reset")
def resetar_manualmente(categoria: str, db: Session = Depends(get_db)):
    # Busca todas as tarefas da categoria atual (Daily ou Weekly)
    tarefas = db.query(models.Tarefa).filter(models.Tarefa.category == categoria).all()
    
    hoje = date.today()
    for t in tarefas:
        t.is_completed = False
        t.last_reset = hoje
        
    db.commit()
    return {"mensagem": f"Todas as tarefas de {categoria} foram resetadas."}

@app.post("/divisorias/", response_model=schemas.Divisoria, status_code=status.HTTP_201_CREATED)
def criar_divisoria(divisoria: schemas.DivisoriaCreate, db: Session = Depends(get_db)):
    db_div = models.Divisoria(nome=divisoria.nome, category=divisoria.category)
    db.add(db_div)
    db.commit()
    db.refresh(db_div)
    return db_div

@app.get("/divisorias/", response_model=List[schemas.Divisoria])
def listar_divisorias(categoria: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Divisoria)
    if categoria:
        query = query.filter(models.Divisoria.category == categoria)
    return query.all()

@app.delete("/divisorias/{divisoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_divisoria(divisoria_id: int, db: Session = Depends(get_db)):
    db_div = db.query(models.Divisoria).filter(models.Divisoria.id == divisoria_id).first()
    if not db_div:
        raise HTTPException(status_code=404, detail="Divisória não encontrada")
    db.delete(db_div)
    db.commit()
    return None

@app.post("/tarefas/", response_model=schemas.Tarefa, status_code=status.HTTP_201_CREATED)
def criar_tarefa(tarefa: schemas.TarefaCreate, db: Session = Depends(get_db)):
    db_tarefa = models.Tarefa(
        title=tarefa.title,
        description=tarefa.description,
        is_completed=tarefa.is_completed,
        category=tarefa.category,
        divisoria_id=tarefa.divisoria_id
    )
    db.add(db_tarefa)
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa