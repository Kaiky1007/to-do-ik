from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from .database import Base

class Divisoria(Base):
    __tablename__ = "divisorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)     
    category = Column(String, nullable=False)
    tarefas = relationship("Tarefa", back_populates="divisoria", cascade="all, delete-orphan")

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    category = Column(String, default="Daily")
    last_reset = Column(Date, default=date.today)
    divisoria_id = Column(Integer, ForeignKey("divisorias.id"), nullable=True)
    divisoria = relationship("Divisoria", back_populates="tarefas")