import tkinter as tk
from tkinter import ttk, messagebox

class VistaSimplex(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Simplex con Pasos (Gran M)")
        self.geometry("900x750")
        self.configure(bg="#F4F6F9")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TLabel", background="#F4F6F9", foreground="#2D3748", font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background="#F4F6F9", foreground="#4A5568", font=("Segoe UI", 10, "bold"))
        self.style.configure("TLabelframe.Label", background="#F4F6F9", foreground="#2B6CB0")
        self.style.configure("Primary.TButton", background="#3182CE", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Primary.TButton", background=[("active", "#2B6CB0")])
        self.style.configure("Secondary.TButton", background="#E2E8F0", foreground="#4A5568", font=("Segoe UI", 9))
        
        self.filas_restricciones = []
        self.controlador = None
        self._crear_componentes()
        
    def _crear_componentes(self):
        self.frame_inputs = ttk.Frame(self, padding=10, width=340, style="TLabel")
        self.frame_inputs.pack(side="left", fill="y")
        self.frame_inputs.pack_propagate(False)
        
        frame_init = ttk.LabelFrame(self.frame_inputs, text=" 1. Variables ", padding=8)
        frame_init.pack(fill="x", pady=5)
        
        ttk.Label(frame_init, text="Num. Variables:").pack(side="left", padx=2)
        self.entry_vars = ttk.Entry(frame_init, width=5, font=("Segoe UI", 10))
        self.entry_vars.pack(side="left", padx=5)
        self.btn_generar = ttk.Button(frame_init, text="Configurar", style="Secondary.TButton")
        self.btn_generar.pack(side="left", padx=5)
        
        self.btn_resolver = ttk.Button(self.frame_inputs, text="⚡ RESOLVER MODELO", state="disabled", style="Primary.TButton")
        self.btn_resolver.pack(fill="x", pady=10)
        
        self.frame_modelo = ttk.LabelFrame(self.frame_inputs, text=" 2. Datos del Modelo ", padding=5)
        self.frame_modelo.pack(fill="both", expand=True, pady=5)
        
        self.canvas = tk.Canvas(self.frame_modelo, borderwidth=0, highlightthickness=0, bg="#F4F6F9")
        self.scrollbar = ttk.Scrollbar(self.frame_modelo, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TLabel")
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        frame_derecho = ttk.LabelFrame(self, text=" Historial de Tableaus (Iteraciones Simplex) ", padding=10)
        frame_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.txt_resultado = tk.Text(frame_derecho, wrap="none", background="#1A202C", fg="#E2E8F0", font=("Consolas", 10), insertbackground="white", padx=10, pady=10)
        scroll_y = ttk.Scrollbar(frame_derecho, orient="vertical", command=self.txt_resultado.yview)
        scroll_x = ttk.Scrollbar(frame_derecho, orient="horizontal", command=self.txt_resultado.xview)
        self.txt_resultado.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.txt_resultado.pack(side="left", fill="both", expand=True)

    def set_controlador(self, controlador):
        self.controlador = controlador
        self.btn_generar.config(command=self.controlador.generar_campos)
        self.btn_resolver.config(command=self.controlador.procesar_y_resolver)
        self.entry_vars.bind("<Return>", lambda e: self.controlador.generar_campos())

    def limpiar_modelo(self):
        for widget in self.scrollable_frame.winfo_children(): 
            widget.destroy()
        self.filas_restricciones = []
        self.btn_resolver.config(state="disabled")

    def mostrar_campos_modelo(self, num_vars):
        ttk.Label(self.scrollable_frame, text="Objetivo de Optimización:").pack(anchor="w", pady=(2, 0))
        self.combo_opt = ttk.Combobox(self.scrollable_frame, values=["Maximizar", "Minimizar"], state="readonly", font=("Segoe UI", 9))
        self.combo_opt.current(0)
        self.combo_opt.pack(fill="x", pady=4)
        
        ttk.Label(self.scrollable_frame, text="Coeficientes de Z:").pack(anchor="w", pady=(10, 0))
        frame_z = ttk.Frame(self.scrollable_frame, style="TLabel")
        frame_z.pack(fill="x", pady=2)
        
        self.entries_z = []
        for i in range(num_vars):
            ttk.Label(frame_z, text=f"X{i+1}:").pack(side="left", padx=(2, 0))
            e = ttk.Entry(frame_z, width=5, font=("Segoe UI", 10))
            e.pack(side="left", padx=2)
            self.entries_z.append(e)
            
        ttk.Label(self.scrollable_frame, text="Restricciones del Problema:").pack(anchor="w", pady=(15, 0))
        self.btn_add_res = ttk.Button(self.scrollable_frame, text="+ Añadir Restricción", command=lambda: self._añadir_y_notificar(num_vars), style="Secondary.TButton")
        self.btn_add_res.pack(anchor="w", pady=5)
        
        self.btn_resolver.config(state="normal")
        self._añadir_y_notificar(num_vars)

    def _añadir_y_notificar(self, num_vars):
        self.añadir_fila_restriccion(num_vars)
        if self.controlador:
            self.controlador.enlazar_eventos_teclado()

    def añadir_fila_restriccion(self, num_vars):
        frame_fila = ttk.Frame(self.scrollable_frame, style="TLabel")
        frame_fila.pack(fill="x", pady=3)
        
        entries_res = []
        for i in range(num_vars):
            e = ttk.Entry(frame_fila, width=4, font=("Segoe UI", 10))
            e.pack(side="left", padx=1)
            entries_res.append(e)
            
        combo_tipo = ttk.Combobox(frame_fila, values=["<=", ">=", "="], width=4, state="readonly", font=("Segoe UI", 9))
        combo_tipo.current(0)
        combo_tipo.pack(side="left", padx=3)
        
        entry_ld = ttk.Entry(frame_fila, width=4, font=("Segoe UI", 10))
        entry_ld.pack(side="left", padx=1)
        
        self.filas_restricciones.append({'coefs': entries_res, 'tipo': combo_tipo, 'ld': entry_ld})

    def mostrar_tablas_en_pantalla(self, texto):
        self.txt_resultado.config(state="normal")
        self.txt_resultado.delete("1.0", tk.END)
        self.txt_resultado.insert(tk.END, texto)
        self.txt_resultado.config(state="disabled")

    def mostrar_error(self, mensaje):
        messagebox.showerror("Error de Entrada", mensaje)
