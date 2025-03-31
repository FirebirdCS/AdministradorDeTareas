import tkinter as tk
from tkinter import ttk, messagebox
import psutil

from process_manager import get_processes, resume_process, suspend_process, terminate_process

class TaskManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Administrador de Tareas")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")
        self.setup_styles()
        self.create_widgets()
        self.refresh_process_list()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=30,
                        fieldbackground="white",
                        font=('Helvetica', 10))
        style.configure("Treeview.Heading",
                        font=('Helvetica', 11, 'bold'),
                        background="#007ACC",
                        foreground="white")
        # Configuración para botones
        style.configure("TButton",
                        font=('Helvetica', 10),
                        padding=5)
        # Configuración para etiquetas
        style.configure("TLabel",
                        font=('Helvetica', 10))

    def create_widgets(self):
        # Frame superior para búsqueda
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)

        ttk.Label(top_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_process_list())

        # Frame central para el Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        columns = ("pid", "name", "cpu", "memory", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="Nombre")
        self.tree.heading("cpu", text="CPU (%)")
        self.tree.heading("memory", text="Memoria (MB)")
        self.tree.heading("status", text="Estado")
        self.tree.column("pid", width=80, anchor=tk.CENTER)
        self.tree.column("name", width=250)
        self.tree.column("cpu", width=100, anchor=tk.CENTER)
        self.tree.column("memory", width=120, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        # Agregar Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Frame inferior para los botones de acción
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)

        self.btn_terminate = ttk.Button(btn_frame, text="Finalizar", command=self.terminate_selected)
        self.btn_terminate.pack(side=tk.LEFT, padx=5)
        self.btn_suspend = ttk.Button(btn_frame, text="Suspender", command=self.suspend_selected)
        self.btn_suspend.pack(side=tk.LEFT, padx=5)
        self.btn_resume = ttk.Button(btn_frame, text="Reanudar", command=self.resume_selected)
        self.btn_resume.pack(side=tk.LEFT, padx=5)
        self.btn_refresh = ttk.Button(btn_frame, text="Refrescar", command=self.refresh_process_list)
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)

    # Método para refrescar la lista de procesos
    def refresh_process_list(self):
        search_text = self.search_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        logical_cpus = psutil.cpu_count(logical=True)

        for proc in get_processes():
            try:
                pid = proc.info['pid']
                name = proc.info['name'] or ""
                if search_text and search_text not in name.lower():
                    continue

                cpu_percent = proc.info['cpu_percent']
                if logical_cpus:
                    cpu_percent = cpu_percent / logical_cpus
                mem = proc.info['memory_info'].rss / (1024 * 1024)
                status = proc.info['status']
                self.tree.insert("", tk.END, values=(
                    pid,
                    name,
                    f"{cpu_percent:.2f}%",
                    f"{mem:.2f}",
                    status
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    # Método para seleccionar un proceso de la lista
    def get_selected_pid(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Selecciona un proceso de la lista.")
            return None
        return self.tree.item(selected[0])["values"][0]

    # Método para terminar un proceso
    def terminate_selected(self):
        pid = self.get_selected_pid()
        if pid is None:
            return
        try:
            terminate_process(pid)
            messagebox.showinfo("Éxito", f"Proceso {pid} finalizado.")
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "El proceso ya no existe.")
        except psutil.AccessDenied:
            messagebox.showerror("Error", "Acceso denegado para finalizar el proceso.")
        except psutil.TimeoutExpired:
            messagebox.showerror("Error", "No se pudo finalizar el proceso a tiempo.")
        self.refresh_process_list()
     # Método para suspender un proceso
    def suspend_selected(self):
        pid = self.get_selected_pid()
        if pid is None:
            return
        try:
            suspend_process(pid)
            messagebox.showinfo("Éxito", f"Proceso {pid} suspendido.")
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "El proceso ya no existe.")
        except psutil.AccessDenied:
            messagebox.showerror("Error", "Acceso denegado para suspender el proceso.")
        self.refresh_process_list()
    # Método para resumir un proceso
    def resume_selected(self):
        pid = self.get_selected_pid()
        if pid is None:
            return
        try:
            resume_process(pid)
            messagebox.showinfo("Éxito", f"Proceso {pid} reanudado.")
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "El proceso ya no existe.")
        except psutil.AccessDenied:
            messagebox.showerror("Error", "Acceso denegado para reanudar el proceso.")
        self.refresh_process_list()
