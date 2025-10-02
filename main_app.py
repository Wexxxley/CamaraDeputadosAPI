<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import os
import webbrowser
import time
import uvicorn

# --- Importações dos módulos ---
from api.tratamentoDados.processador import run_data_processing
from api.main import app as fastapi_app

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador Parlamentar")
        self.root.geometry("650x500")
        self.root.configure(bg="#1e2a38")

        # Fila para comunicação segura entre a thread de trabalho e a GUI
        self.queue = queue.Queue()

        self.setup_styles()
        self.create_widgets()
        self.root.after(100, self.process_queue)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e2a38")
        style.configure("TLabel", background="#1e2a38", foreground="#f7c873", font=("Segoe UI", 12, "bold"))
        style.configure("Header.TLabel", background="#1e2a38", foreground="#f7c873", font=("Segoe UI", 18, "bold"))
        style.configure("TButton", background="#f7c873", foreground="#1e2a38", font=("Segoe UI", 12, "bold"))
        style.map("TButton", background=[("active", "#f7c873")])
        style.configure("TCombobox", fieldbackground="#f7c873", background="#f7c873", foreground="#1e2a38", font=("Segoe UI", 12))
        style.configure("TProgressbar", troughcolor="#f7c873", background="#1e2a38", thickness=20)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Header ---
        ttk.Label(main_frame, text="Analisador Parlamentar", style="Header.TLabel").pack(pady=(0, 10))

        # --- Seção de Input ---
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        ttk.Label(input_frame, text="Selecione o Ano:").pack(side=tk.LEFT, padx=(0, 5))
        self.year_combobox = ttk.Combobox(
            input_frame,
            values=[str(y) for y in range(2011, 2025)],
            state="readonly",
            width=10,
            style="TCombobox"
        )
        self.year_combobox.pack(side=tk.LEFT)
        self.year_combobox.current(0)
        self.start_button = ttk.Button(input_frame, text="Iniciar Processamento", command=self.start_process_thread)
        self.start_button.pack(side=tk.RIGHT, padx=(10, 0))

        # --- Seção de Progresso ---
        ttk.Label(main_frame, text="Progresso:").pack(anchor=tk.W, pady=(15, 0))
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate', length=400, style="TProgressbar", maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=4)

        # --- Seção de Log ---
        ttk.Label(main_frame, text="Log de Atividades:").pack(anchor=tk.W, pady=(15, 0))
        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, font=("Consolas", 11), bg="#263445", fg="#f7c873", insertbackground="#f7c873")
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=2)
        self.log_area.configure(state='disabled')

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def process_queue(self):
        try:
            while not self.queue.empty():
                message_type, data = self.queue.get_nowait()
                if message_type == 'log':
                    self.log(data)
                elif message_type == 'progress':
                    self.progress_bar['value'] = data
                elif message_type == 'done':
                    self.start_button.config(state="normal")
                    self.log(">>> PROCESSO FINALIZADO <<<")
        finally:
            self.root.after(100, self.process_queue)

    def start_process_thread(self):
        year_str = self.year_combobox.get()
        if not year_str.isdigit():
            self.log("Erro: Por favor, selecione um ano válido.")
            return

        self.start_button.config(state="disabled")
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100  # Reset maximum for each run
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.configure(state='disabled')

        threading.Thread(
            target=self.main_orchestrator,
            args=(int(year_str),),
            daemon=True
        ).start()

    def main_orchestrator(self, year):
        def progress_callback(msg_type, data):
            self.queue.put((msg_type, data))

        try:
            success = run_data_processing(year, progress_callback)
            if not success:
                raise Exception("O processamento de dados falhou.")

            self.queue.put(('log', "Iniciando servidor da API local..."))
            os.environ['DATABASE_YEAR'] = str(year)

            api_thread = threading.Thread(
                target=lambda: uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning"),
                daemon=True
            )
            api_thread.start()
            time.sleep(5)
            self.queue.put(('log', "API rodando em http://127.0.0.1:8000"))

            self.queue.put(('log', "Abrindo a interface de visualização..."))
            html_file_path = os.path.join("frontend", "index.html")
            webbrowser.open(f'file://{os.path.realpath(html_file_path)}?year={year}')

        except Exception as e:
            self.queue.put(('log', f"ERRO CRÍTICO: {e}"))
        finally:
            self.queue.put(('done', None))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
=======
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import os
import webbrowser
import time
import uvicorn

# --- Importações dos módulos ---
from tratamentoDados.processador import run_data_processing
from api.main import app as fastapi_app

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador Parlamentar")
        self.root.geometry("600x450")

        # Fila para comunicação segura entre a thread de trabalho e a GUI
        self.queue = queue.Queue()

        self.create_widgets()
        
        # Inicia o loop que verifica a fila por mensagens
        self.root.after(100, self.process_queue)

    def create_widgets(self):
        """Cria e posiciona todos os componentes visuais na janela."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seção de Input ---
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        ttk.Label(input_frame, text="Ano:").pack(side=tk.LEFT, padx=(0, 5))
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.pack(side=tk.LEFT)
        self.start_button = ttk.Button(input_frame, text="Iniciar Processamento", command=self.start_process_thread)
        self.start_button.pack(side=tk.RIGHT)

        # --- Seção de Progresso ---
        ttk.Label(main_frame, text="Progresso:").pack(anchor=tk.W, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=2)

        # --- Seção de Log ---
        ttk.Label(main_frame, text="Log de Atividades:").pack(anchor=tk.W, pady=(10, 0))
        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=2)
        self.log_area.configure(state='disabled')

    def log(self, message):
        """Adiciona uma mensagem à área de log de forma segura."""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END) # Auto-scroll
        self.log_area.configure(state='disabled')

    def process_queue(self):
        """Processa mensagens da fila enviadas pela thread de trabalho."""
        try:
            while not self.queue.empty():
                message_type, data = self.queue.get_nowait()
                if message_type == 'log':
                    self.log(data)
                elif message_type == 'progress':
                    self.progress_bar['value'] = data
                elif message_type == 'done':
                    self.start_button.config(state="normal")
                    self.log(">>> PROCESSO FINALIZADO <<<")
        finally:
            self.root.after(100, self.process_queue)

    def start_process_thread(self):
        """Inicia a thread principal que orquestra todo o trabalho."""
        year_str = self.year_entry.get()
        if not year_str.isdigit():
            self.log("Erro: Por favor, insira um ano válido.")
            return

        self.start_button.config(state="disabled")
        self.progress_bar['value'] = 0
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.configure(state='disabled')
        
        # A thread principal chama o orquestrador
        threading.Thread(
            target=self.main_orchestrator,
            args=(int(year_str),),
            daemon=True
        ).start()

    def main_orchestrator(self, year):
        """
        Esta é a função principal que executa a sequência de tarefas.
        Roda em uma thread separada para não travar a GUI.
        """
        def progress_callback(msg_type, data):
            """Função de callback para ser passada para o processador de dados."""
            self.queue.put((msg_type, data))

        try:
            # --- 1. CHAMAR O TRATAMENTO DE DADOS ---
            success = run_data_processing(year, progress_callback)
            if not success:
                raise Exception("O processamento de dados falhou.")

            # --- 2. INICIAR A API ---
            self.queue.put(('log', "Iniciando servidor da API local..."))
            os.environ['DATABASE_YEAR'] = str(year)
            
            # A API Uvicorn precisa rodar em sua própria thread para não bloquear
            api_thread = threading.Thread(
                target=lambda: uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning"),
                daemon=True
            )
            api_thread.start()
            time.sleep(5) # Pausa para garantir que o servidor iniciou
            self.queue.put(('log', "API rodando em http://127.0.0.1:8000"))

            # --- 3. ABRIR O NAVEGADOR ---
            self.queue.put(('log', "Abrindo a interface de visualização..."))
            html_file_path = os.path.join("frontend", "index.html")
            webbrowser.open(f'file://{os.path.realpath(html_file_path)}')

        except Exception as e:
            self.queue.put(('log', f"ERRO CRÍTICO: {e}"))
        finally:
            # Envia a mensagem de finalização para reativar o botão
            self.queue.put(('done', None))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()


    
>>>>>>> origin/Refatorando
