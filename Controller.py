from Model import ModeloSimplex
from View import VistaSimplex

class ControladorSimplex:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.num_vars = 0

    def generar_campos(self):
        try:
            self.num_vars = int(self.vista.entry_vars.get())
            if self.num_vars <= 0: raise ValueError()
        except ValueError:
            self.vista.mostrar_error("Introduce un número entero de variables mayor a 0.")
            return
        self.vista.limpiar_modelo()
        self.vista.mostrar_campos_modelo(self.num_vars)

    def enlazar_eventos_teclado(self):
        lista_campos = []
        lista_campos.extend(self.vista.entries_z)
        for fila in self.vista.filas_restricciones:
            lista_campos.extend(fila['coefs'])
            lista_campos.append(fila['ld'])
            
        for campo in lista_campos:
            campo.unbind("<Return>")
            
        for idx, campo_actual in enumerate(lista_campos):
            if idx == len(lista_campos) - 1:
                campo_actual.bind("<Return>", lambda e: self.procesar_y_resolver())
            else:
                siguiente_campo = lista_campos[idx + 1]
                campo_actual.bind("<Return>", lambda e, act=campo_actual, sig=siguiente_campo: self._manejar_salto_enter(act, sig))

    def _manejar_salto_enter(self, actual, siguiente):
        if not actual.get().strip():
            actual.delete(0, "end")
            actual.insert(0, "0")
        siguiente.focus_set()
        siguiente.icursor("end")

    def procesar_y_resolver(self):
        try:
            tipo = 'max' if self.vista.combo_opt.get() == "Maximizar" else 'min'
            coefs_z = [float(e.get()) if e.get().strip() else 0.0 for e in self.vista.entries_z]
            
            restricciones_list = []
            for fila in self.vista.filas_restricciones:
                ld_val = fila['ld'].get().strip()
                if not ld_val:
                    ld_val = "0.0"
                    fila['ld'].insert(0, "0")
                    
                restricciones_list.append({
                    'coefs': [float(e.get()) if e.get().strip() else 0.0 for e in fila['coefs']],
                    'tipo': fila['tipo'].get(),
                    'ld': float(ld_val)
                })
        except ValueError:
            self.vista.mostrar_error("Por favor ingresa únicamente valores numéricos.")
            return

        resultado = self.modelo.resolver_gran_m(tipo, coefs_z, restricciones_list)
        
        salida_visual = ""
        for idx, tabla in enumerate(resultado['tablas']):
            salida_visual += f"┌────────────────────────────────────────────────────────┐\n"
            salida_visual += f"│               TABLEAU ITERACIÓN #{idx:<3}                  │\n"
            salida_visual += f"└────────────────────────────────────────────────────────┘\n"
            
            # CORRECCIÓN EN EL CÁLCULO DEL ANCHO DE COLUMNAS:
            num_columnas = len(tabla[0])
            anchos = [max(len(fila[col]) for fila in tabla) for col in range(num_columnas)]
            
            for fila in tabla:
                linea = " │ ".join(f"{celda:<{anchos[col]}}" for col, celda in enumerate(fila))
                salida_visual += f"  {linea}\n"
            salida_visual += "─" * (sum(anchos) + (len(anchos) * 3)) + "\n\n"
            
        if resultado['exito']:
            salida_visual += f"🏆 SOLUCIÓN ÓPTIMA ENCONTRADA\n"
            salida_visual += f"=============================\n"
            salida_visual += f" Valor óptimo Z = {resultado['z']}\n"
            for i, v in enumerate(resultado['variables']):
                salida_visual += f" Variable X{i+1} = {v}\n"
        else:
            salida_visual += f"❌ ALERTA: {resultado['mensaje']}\n"
            
        self.vista.mostrar_tablas_en_pantalla(salida_visual)

if __name__ == "__main__":
    modelo_app = ModeloSimplex()
    vista_app = VistaSimplex()
    controlador_app = ControladorSimplex(modelo_app, vista_app)
    vista_app.set_controlador(controlador_app)
    vista_app.mainloop()
