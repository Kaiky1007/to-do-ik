import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QListWidget, 
    QLabel, QCheckBox, QListWidgetItem, QTabWidget, QStyle,
    QSizeGrip, QSystemTrayIcon, QMenu, QInputDialog, QScrollArea, QMessageBox
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt

API_URL_TAREFAS = "http://127.0.0.1:8000/tarefas/"
API_URL_DIVISORIAS = "http://127.0.0.1:8000/divisorias/"

# =================================================================
# CLASSE CUSTOMIZADA PARA O DRAG & DROP
# =================================================================
class KanbanListWidget(QListWidget):
    def __init__(self, divisoria_id, main_window):
        super().__init__()
        self.divisoria_id = divisoria_id
        self.main_window = main_window
        
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QListWidget.SingleSelection)

    def dragEnterEvent(self, event):
        if isinstance(event.source(), KanbanListWidget):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        source_widget = event.source()
        if isinstance(source_widget, KanbanListWidget):
            item = source_widget.currentItem()
            if item:
                task_id = item.data(Qt.UserRole)
                if source_widget != self:
                    self.main_window.mover_tarefa(task_id, self.divisoria_id)
        event.ignore() 
# =================================================================


class TodoWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("To-Do Widget")
        self.setMinimumSize(450, 500) 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.oldPos = None
        self.is_minimized = False
        self.normal_height = 500
        
        self.divisorias_atuais = []

        self.setStyleSheet("""
            QMainWindow { background-color: #121212; border-radius: 10px; }
            QWidget { color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; }
            
            QLineEdit { background-color: #1e1e1e; border: 1px solid #333333; border-radius: 5px; padding: 8px; }
            QLineEdit:focus { border: 1px solid #6200ea; }
            
            QPushButton { background-color: #6200ea; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold; }
            QPushButton:hover { background-color: #7c4dff; }
            
            #btn_reset { background-color: #333333; padding: 8px; border-radius: 5px; color: #aaaaaa; }
            #btn_reset:hover { background-color: #555555; color: white; }
            
            #btn_add_corner { 
                background-color: #333333; 
                border-radius: 5px; 
                color: #aaaaaa; 
                font-weight: bold; 
                font-size: 18px;
                padding: 0px; 
            }
            #btn_add_corner:hover { background-color: #555555; color: white; }
            
            QTabWidget::pane { border: none; }
            QTabBar::tab { background-color: #1e1e1e; color: #888; padding: 8px 20px; border-radius: 5px; margin-right: 2px; margin-bottom: 5px; }
            QTabBar::tab:selected { background-color: #6200ea; color: white; font-weight: bold; }
            
            QScrollArea { border: none; background-color: #161616; border-radius: 10px; }
            
            .ColunaWidget { background-color: #1a1a1a; border-radius: 8px; border: 1px solid #2a2a2a; }
            
            QListWidget { background-color: transparent; border: none; outline: none; }
            QListWidget::item { border-bottom: 1px solid #2c2c2c; }
            QListWidget::item:selected { background-color: transparent; }
            
            QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #6200ea; border-radius: 4px; background-color: transparent; }
            QCheckBox::indicator:checked { background-color: #6200ea; }
            
            #btn_controle { background-color: transparent; color: #888; font-weight: bold; font-size: 16px; padding: 0px 5px;}
            #btn_controle:hover { color: #ffffff; }
            #btn_fechar_coluna { background-color: transparent; color: #888; font-weight: bold; font-size: 14px; padding: 0px;}
            #btn_fechar_coluna:hover { color: #ff5252; }
            #btn_deletar_item { background-color: transparent; color: #ff5252; font-weight: bold; font-size: 14px; padding: 4px; border-radius: 4px;}
            #btn_deletar_item:hover { background-color: #2a2a2a; }
        """)

        self.setup_ui()
        self.setup_tray_icon()
        self.carregar_tudo()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 5)

        # Cabeçalho
        header_layout = QHBoxLayout()
        titulo_label = QLabel("Minhas Tarefas")
        titulo_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        self.btn_minimizar = QPushButton("–")
        self.btn_minimizar.setObjectName("btn_controle")
        self.btn_minimizar.clicked.connect(self.alternar_minimizar)

        btn_fechar = QPushButton("X")
        btn_fechar.setObjectName("btn_controle")
        btn_fechar.clicked.connect(self.hide)
        
        header_layout.addWidget(titulo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_minimizar)
        header_layout.addWidget(btn_fechar)
        self.main_layout.addLayout(header_layout)

        # Conteúdo
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Input e Botões
        input_layout = QHBoxLayout()
        self.input_tarefa = QLineEdit()
        self.input_tarefa.setPlaceholderText("Nova tarefa...")
        
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_reset.setToolTip("Resetar as tarefas desta aba")
        self.btn_reset.setObjectName("btn_reset") 
        
        input_layout.addWidget(self.input_tarefa)
        input_layout.addWidget(self.btn_adicionar)
        input_layout.addWidget(self.btn_reset)

        # Sistema de Abas
        self.tabs = QTabWidget()
        
        self.btn_add_corner = QPushButton("+")
        self.btn_add_corner.setObjectName("btn_add_corner")
        self.btn_add_corner.setToolTip("Adicionar nova coluna")
        self.btn_add_corner.setFixedSize(30, 30) 
        self.btn_add_corner.clicked.connect(self.adicionar_coluna_aba_atual)
        
        corner_container = QWidget()
        corner_layout = QHBoxLayout(corner_container)
        corner_layout.setContentsMargins(0, 0, 15, 5) 
        corner_layout.addWidget(self.btn_add_corner)
        
        self.tabs.setCornerWidget(corner_container, Qt.TopRightCorner)
        
        # Aba Daily
        self.tab_daily = QWidget()
        layout_daily = QVBoxLayout(self.tab_daily)
        layout_daily.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_daily = QScrollArea()
        self.scroll_daily.setWidgetResizable(True)
        self.scroll_daily.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.container_daily = QWidget()
        self.layout_colunas_daily = QHBoxLayout(self.container_daily)
        self.layout_colunas_daily.setAlignment(Qt.AlignLeft)
        self.scroll_daily.setWidget(self.container_daily)
        
        layout_daily.addWidget(self.scroll_daily)

        # Aba Weekly
        self.tab_weekly = QWidget()
        layout_weekly = QVBoxLayout(self.tab_weekly)
        layout_weekly.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_weekly = QScrollArea()
        self.scroll_weekly.setWidgetResizable(True)
        self.scroll_weekly.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.container_weekly = QWidget()
        self.layout_colunas_weekly = QHBoxLayout(self.container_weekly)
        self.layout_colunas_weekly.setAlignment(Qt.AlignLeft)
        self.scroll_weekly.setWidget(self.container_weekly)
        
        layout_weekly.addWidget(self.scroll_weekly)

        self.tabs.addTab(self.tab_daily, "Daily")
        self.tabs.addTab(self.tab_weekly, "Weekly")

        # Rodapé
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addStretch() 
        size_grip = QSizeGrip(self)
        size_grip.setStyleSheet("width: 15px; height: 15px;") 
        footer_layout.addWidget(size_grip)

        content_layout.addSpacing(10)
        content_layout.addLayout(input_layout)
        content_layout.addWidget(self.tabs)
        content_layout.addLayout(footer_layout)

        self.main_layout.addWidget(self.content_widget)

        # Eventos
        self.btn_adicionar.clicked.connect(self.adicionar_tarefa)
        self.input_tarefa.returnPressed.connect(self.adicionar_tarefa)
        self.btn_reset.clicked.connect(self.resetar_aba_manualmente)

    # --- LÓGICA DE INTERFACE E DADOS ---

    def limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def carregar_tudo(self):
        self.limpar_layout(self.layout_colunas_daily)
        self.limpar_layout(self.layout_colunas_weekly)
        
        try:
            resposta = requests.get(API_URL_DIVISORIAS)
            if resposta.status_code == 200:
                self.divisorias_atuais = resposta.json()
                
                for div in self.divisorias_atuais:
                    if div['category'] == "Daily":
                        self.desenhar_coluna_kanban(div, self.layout_colunas_daily)
                    elif div['category'] == "Weekly":
                        self.desenhar_coluna_kanban(div, self.layout_colunas_weekly)
        except requests.exceptions.ConnectionError:
            print("⚠️ Erro de conexão.")

    def desenhar_coluna_kanban(self, divisoria, layout_pai):
        coluna_widget = QWidget()
        coluna_widget.setMinimumWidth(220)
        coluna_widget.setProperty("class", "ColunaWidget") 
        
        coluna_layout = QVBoxLayout(coluna_widget)
        coluna_layout.setContentsMargins(5, 5, 5, 5)
        
        header_coluna = QHBoxLayout()
        lbl_titulo = QLabel(divisoria['nome'])
        lbl_titulo.setAlignment(Qt.AlignCenter) 
        lbl_titulo.setStyleSheet("font-weight: bold; color: #aaa;")
        
        btn_deletar_coluna = QPushButton("X")
        btn_deletar_coluna.setObjectName("btn_fechar_coluna")
        btn_deletar_coluna.setFixedSize(20, 20) 
        btn_deletar_coluna.clicked.connect(lambda _, did=divisoria['id']: self.deletar_divisoria_db(did))
        
        header_coluna.addWidget(lbl_titulo, stretch=1) 
        header_coluna.addWidget(btn_deletar_coluna)
        
        lista_tarefas = KanbanListWidget(divisoria['id'], self)
        
        for tarefa in divisoria['tarefas']:
            self.desenhar_item_tarefa(tarefa, lista_tarefas)
            
        coluna_layout.addLayout(header_coluna)
        coluna_layout.addWidget(lista_tarefas)
        
        layout_pai.addWidget(coluna_widget)
        
    def desenhar_item_tarefa(self, tarefa, lista_destino):
        item = QListWidgetItem(lista_destino)
        item.setData(Qt.UserRole, tarefa['id'])
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(2, 2, 2, 2)

        checkbox = QCheckBox()
        checkbox.setChecked(tarefa['is_completed'])
        checkbox.toggled.connect(lambda checked, tid=tarefa['id']: self.atualizar_status(tid, checked))

        label_titulo = QLabel(tarefa['title'])
        if tarefa['is_completed']:
            label_titulo.setStyleSheet("color: #666666; text-decoration: line-through;")

        btn_deletar = QPushButton("X")
        btn_deletar.setObjectName("btn_deletar_item")
        btn_deletar.setFixedSize(24, 24)
        btn_deletar.clicked.connect(lambda _, tid=tarefa['id']: self.deletar_tarefa(tid))

        row_layout.addWidget(checkbox)
        row_layout.addWidget(label_titulo)
        row_layout.addStretch()
        row_layout.addWidget(btn_deletar)

        item.setSizeHint(row_widget.sizeHint())
        lista_destino.setItemWidget(item, row_widget)

    # --- COMUNICAÇÃO COM A API ---

    def adicionar_coluna_aba_atual(self):
        aba_atual = self.tabs.tabText(self.tabs.currentIndex())
        self.criar_nova_divisoria_db(aba_atual)

    def criar_nova_divisoria_db(self, categoria):
        nome, ok = QInputDialog.getText(self, "Nova Coluna", "Nome da Coluna:")
        if ok and nome.strip():
            dados = {"nome": nome.strip(), "category": categoria}
            try:
                requests.post(API_URL_DIVISORIAS, json=dados)
                self.carregar_tudo()
            except:
                print("Erro ao criar divisória")

    def deletar_divisoria_db(self, divisoria_id):
        resposta = QMessageBox.question(self, "Confirmar", "Isso apagará a coluna e todas as tarefas dentro dela. Continuar?", QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            try:
                requests.delete(f"{API_URL_DIVISORIAS}{divisoria_id}")
                self.carregar_tudo()
            except:
                print("Erro ao deletar divisória")

    # --- ALTERAÇÃO AQUI: LÓGICA DA COLUNA INVISÍVEL ---
    def adicionar_tarefa(self):
        titulo = self.input_tarefa.text().strip()
        if not titulo: return
            
        aba_atual = self.tabs.tabText(self.tabs.currentIndex())
        colunas_da_aba = [d for d in self.divisorias_atuais if d['category'] == aba_atual]
        
        # Se não houver coluna, criamos a "Geral" automaticamente
        if not colunas_da_aba:
            dados_coluna = {"nome": "Geral", "category": aba_atual}
            try:
                resposta_coluna = requests.post(API_URL_DIVISORIAS, json=dados_coluna)
                if resposta_coluna.status_code == 201: # 201 Created
                    nova_coluna = resposta_coluna.json()
                    divisoria_id = nova_coluna['id']
                else:
                    return # Sai se algo estranho acontecer
            except requests.exceptions.ConnectionError:
                print("Erro de conexão ao criar coluna padrão.")
                return
        else:
            # Pega a primeira coluna existente (Caixa de Entrada)
            divisoria_id = colunas_da_aba[0]['id']
        
        # Finalmente, cria a tarefa amarrada ao ID da coluna (nova ou velha)
        dados_tarefa = {"title": titulo, "category": aba_atual, "divisoria_id": divisoria_id}
        
        try:
            requests.post(API_URL_TAREFAS, json=dados_tarefa)
            self.input_tarefa.clear()
            self.carregar_tudo() # O carregar_tudo vai redesenhar a tela inteira (incluindo a coluna nova, se foi criada)
        except requests.exceptions.ConnectionError:
            print("Erro ao criar tarefa.")

    def atualizar_status(self, task_id, is_completed):
        try:
            requests.put(f"{API_URL_TAREFAS}{task_id}", json={"is_completed": is_completed})
            self.carregar_tudo()
        except: pass
        
    def mover_tarefa(self, task_id, novo_divisoria_id):
        try:
            requests.put(f"{API_URL_TAREFAS}{task_id}", json={"divisoria_id": novo_divisoria_id})
            self.carregar_tudo()
        except: pass

    def deletar_tarefa(self, task_id):
        try:
            requests.delete(f"{API_URL_TAREFAS}{task_id}")
            self.carregar_tudo()
        except: pass

    def resetar_aba_manualmente(self):
        aba_atual = self.tabs.tabText(self.tabs.currentIndex())
        try:
            requests.post(f"{API_URL_TAREFAS}reset?categoria={aba_atual}")
            self.carregar_tudo()
        except: pass

    # --- FUNÇÕES DE JANELA (Minimizar, Tray, Arrastar) ---
    def alternar_minimizar(self):
        if not self.is_minimized:
            self.normal_height = self.height()
            self.content_widget.hide()
            self.main_layout.setContentsMargins(15, 15, 15, 15)
            self.setMinimumSize(450, 0)
            self.resize(self.width(), 0)
            self.btn_minimizar.setText("+")
            self.is_minimized = True
        else:
            self.content_widget.show()
            self.main_layout.setContentsMargins(15, 15, 15, 5)
            self.setMinimumSize(450, 500)
            self.resize(self.width(), self.normal_height)
            self.btn_minimizar.setText("–")
            self.is_minimized = False

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        tray_menu = QMenu()
        acao_mostrar = QAction("Mostrar/Ocultar Widget", self)
        acao_mostrar.triggered.connect(self.alternar_janela)
        tray_menu.addAction(acao_mostrar)
        tray_menu.addSeparator() 
        acao_sair = QAction("Sair", self)
        acao_sair.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(acao_sair)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_clicado)

    def alternar_janela(self):
        if self.isVisible(): self.hide()
        else: self.showNormal(); self.activateWindow()

    def tray_clicado(self, reason):
        if reason == QSystemTrayIcon.DoubleClick: self.alternar_janela()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.oldPos: return
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.pos() + delta)
        self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event): self.oldPos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    janela = TodoWidget()
    janela.show()
    sys.exit(app.exec())