import numpy as np

class ModeloSimplex:
    def __init__(self):
        self.historico_tablas = []
        
    def resolver_gran_m(self, tipo_opt, c_user, restricciones):
        self.historico_tablas = []
        num_vars_originales = len(c_user)
        
        num_holguras = 0
        num_artificiales = 0
        for res in restricciones:
            if res['tipo'] == '<=': num_holguras += 1
            elif res['tipo'] == '>=': num_holguras += 1; num_artificiales += 1
            elif res['tipo'] == '=': num_artificiales += 1
            
        total_columnas = num_vars_originales + num_holguras + num_artificiales
        c_extendido = np.zeros((total_columnas, 2))
        
        for i in range(num_vars_originales):
            c_extendido[i, 1] = c_user[i] if tipo_opt == 'min' else -c_user[i]
            
        idx_art_cost = num_vars_originales + num_holguras
        for _ in range(num_artificiales):
            c_extendido[idx_art_cost, 0] = 1.0
            idx_art_cost += 1

        matriz_A = np.zeros((len(restricciones), total_columnas))
        vector_b = np.zeros(len(restricciones))
        variables_base = []
        
        curr_h = num_vars_originales
        curr_a = num_vars_originales + num_holguras
        
        for idx_res, res in enumerate(restricciones):
            for j in range(num_vars_originales):
                matriz_A[idx_res, j] = res['coefs'][j]
            vector_b[idx_res] = res['ld']
            
            if res['tipo'] == '<=':
                matriz_A[idx_res, curr_h] = 1.0
                variables_base.append(curr_h)
                curr_h += 1
            elif res['tipo'] == '>=':
                matriz_A[idx_res, curr_h] = -1.0
                matriz_A[idx_res, curr_a] = 1.0
                variables_base.append(curr_a)
                curr_h += 1
                curr_a += 1
            elif res['tipo'] == '=':
                matriz_A[idx_res, curr_a] = 1.0
                variables_base.append(curr_a)
                curr_a += 1

        num_filas = len(restricciones) + 1
        num_cols = total_columnas + 1
        tabla = np.zeros((num_filas, num_cols, 2))
        
        for i in range(len(restricciones)):
            for j in range(total_columnas):
                tabla[i, j, 1] = matriz_A[i, j]
            tabla[i, -1, 1] = vector_b[i]
            
        for j in range(num_cols):
            val_M = 0.0
            val_ind = 0.0
            for i, base_var in enumerate(variables_base):
                val_M += tabla[i, j, 0] * c_extendido[base_var, 0]
                coef_base_m = c_extendido[base_var, 0]
                if coef_base_m != 0:
                    val_M += tabla[i, j, 1] * coef_base_m
                    val_ind += tabla[i, j, 1] * c_extendido[base_var, 1]
            
            if j < total_columnas:
                tabla[-1, j, 0] = val_M - c_extendido[j, 0]
                tabla[-1, j, 1] = val_ind - c_extendido[j, 1]
            else:
                tabla[-1, j, 0] = val_M
                tabla[-1, j, 1] = val_ind

        self._guardar_tabla(tabla, variables_base, num_vars_originales)




# Algoritmo Primal Simplex Iterativo
        iteracion = 0
        max_iter = 50
        while iteracion < max_iter:
            col_entrante = -1
            max_m = -1e-9
            max_ind = -1e-9
            
            for j in range(total_columnas):
                m_f = tabla[-1, j, 0]
                ind_f = tabla[-1, j, 1]
                if m_f > max_m or (abs(m_f - max_m) < 1e-9 and ind_f > max_ind):
                    if m_f > 1e-9 or (abs(m_f) < 1e-9 and ind_f > 1e-9):
                        max_m = m_f
                        max_ind = ind_f
                        col_entrante = j
                        
            if col_entrante == -1:
                break
                
            fila_saliente = -1
            min_razon = float('inf')
            for i in range(len(restricciones)):
                denominador = tabla[i, col_entrante, 1]
                if denominador > 1e-9:
                    razon = tabla[i, -1, 1] / denominador
                    if razon < min_razon:
                        min_razon = razon
                        fila_saliente = i
                        
            if fila_saliente == -1:
                return {'exito': False, 'mensaje': "El problema no está acotado.", 'tablas': self.historico_tablas}
                
            pivote = tabla[fila_saliente, col_entrante, 1]
            tabla[fila_saliente, :, :] /= pivote
            variables_base[fila_saliente] = col_entrante
            
            for i in range(num_filas):
                if i != fila_saliente:
                    factor_m = tabla[i, col_entrante, 0]
                    factor_ind = tabla[i, col_entrante, 1]
                    if abs(factor_m) > 1e-9 or abs(factor_ind) > 1e-9:
                        for j in range(num_cols):
                            tabla[i, j, 0] -= factor_m * tabla[fila_saliente, j, 1]
                            tabla[i, j, 1] -= factor_ind * tabla[fila_saliente, j, 1]
            
            self._guardar_tabla(tabla, variables_base, num_vars_originales)
            iteracion += 1

        z_final = tabla[-1, -1, 1] if tipo_opt == 'min' else -tabla[-1, -1, 1]
        z_m = tabla[-1, -1, 0]
        if abs(z_m) > 1e-4:
            return {'exito': False, 'mensaje': "El problema no tiene solución factible.", 'tablas': self.historico_tablas}

        valores_variables = [0.0] * num_vars_originales
        for i, var_idx in enumerate(variables_base):
            if var_idx < num_vars_originales:
                valores_variables[var_idx] = tabla[i, -1, 1]

        return {
            'exito': True,
            'z': round(z_final, 4),
            'variables': [round(v, 4) for v in valores_variables],
            'tablas': self.historico_tablas
        }




#Formateador Algebraico de Celdas
    def _guardar_tabla(self, tabla, variables_base, num_vars_originales):
        filas_str = []
        for i in range(tabla.shape[0] - 1):
            fila_txt = [f"X{variables_base[i]+1}"]
            for j in range(tabla.shape[1]):
                m, ind = tabla[i, j, 0], tabla[i, j, 1]
                fila_txt.append(self._formato_celda(m, ind))
            filas_str.append(fila_txt)
            
        fila_z = ["Z"]
        for j in range(tabla.shape[1]):
            m, ind = tabla[-1, j, 0], tabla[-1, j, 1]
            fila_z.append(self._formato_celda(m, ind))
        filas_str.append(fila_z)
        self.historico_tablas.append(filas_str)

    def _formato_celda(self, m, b):
        if abs(m) < 1e-4: return f"{round(b, 2)}"
        if abs(b) < 1e-4: return f"{round(m, 2)}M"
        signo = "+" if b > 0 else "-"
        return f"{round(m, 2)}M {signo} {round(abs(b), 2)}"
