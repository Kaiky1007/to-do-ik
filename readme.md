# Kanban To-Do Widget 📝

Um widget de produtividade nativo para Desktop inspirado na metodologia Kanban. Este projeto divide-se em uma interface gráfica (Frontend) minimalista e flutuante, e uma API RESTful (Backend) responsável pelo gerenciamento de dados e persistência.

O aplicativo permite o gerenciamento rápido de tarefas diárias e semanais através de um sistema prático de Drag & Drop (arrastar e soltar), rodando silenciosamente na bandeja do sistema (System Tray).

## 🚀 Funcionalidades

* **Design Minimalista:** Janela *frameless* (sem bordas) com tema escuro (Dark Mode) que se integra perfeitamente à área de trabalho.
* **Sistema Kanban:** Crie colunas (divisórias) e organize suas tarefas visualmente.
* **Drag & Drop:** Arraste tarefas livremente entre as colunas para atualizar seus status.
* **Lazy Creation:** Se uma tarefa for adicionada sem uma coluna pré-existente, o sistema cria automaticamente uma coluna "Geral" (Caixa de Entrada).
* **System Tray:** O widget pode ser minimizado para a bandeja do sistema do SO, rodando em segundo plano sem poluir a barra de tarefas.
* **Modo Compacto:** Botão de minimização em linha que reduz o aplicativo a uma pequena barra superior.
* **Sincronização em Tempo Real:** Comunicação direta com a API para persistência instantânea de dados (Check/Uncheck, Deletar, Mover).

## 🛠️ Tecnologias Utilizadas

### Frontend (Desktop)
* **Python 3.10+**
* **PySide6 (Qt for Python):** Utilizado para a construção de toda a interface gráfica e eventos nativos do SO.
* **PyInstaller:** Para empacotamento da aplicação em um executável autônomo (`.exe`).

### Backend (API & Banco de Dados)
* **FastAPI:** Framework web assíncrono para construção ágil da API RESTful.
* **Uvicorn:** Servidor ASGI para rodar a aplicação.
* **SQLAlchemy:** ORM para mapeamento e comunicação com o banco de dados.
* **PostgreSQL:** Banco de dados relacional principal.
* **Docker & Docker Compose:** Containerização do ambiente de desenvolvimento (API + Banco de Dados).

## ⚙️ Arquitetura do Projeto

O projeto é dividido em dois ecossistemas que se comunicam via requisições HTTP:
1. **Backend:** Fornece as rotas `/tarefas/` e `/divisorias/` para o CRUD completo.
2. **Frontend:** Consome a API e renderiza os dados em tempo real utilizando componentes customizados do PySide6.

## 💻 Como Executar Localmente


### 1. Subindo o Backend (API + Banco de Dados Local)
Navegue até a pasta do backend. O projeto conta com um `docker-compose.yml` pré-configurado que cria um contêiner do PostgreSQL e compila a API automaticamente numa rede interna.

No terminal, execute:
```bash
docker compose up -d --build
```
A API estará configurada e disponível em `http://127.0.0.1:8000`.

### 2. Rodando o Frontend
Em um terminal separado (recomenda-se o uso de um ambiente virtual Python), instale as dependências da interface:
```bash
pip install PySide6 requests
```
Inicie o widget:
```bash
python main_window.py
```
*(Nota: Certifique-se de que as variáveis `API_URL_TAREFAS` e `API_URL_DIVISORIAS` no arquivo `main_window.py` estejam apontando para `http://127.0.0.1:8000` durante os testes locais).*