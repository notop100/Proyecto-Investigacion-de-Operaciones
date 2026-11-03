# Proyecto Investigación de Operaciones

Calculadora de programación lineal con interfaz gráfica que muestra el procedimiento **paso a paso** (tabla por tabla). Hecha en Python con Tkinter,
siguiendo el patrón MVC.

## Estado del proyecto

- [x] Método de la **Gran M** (restricciones `<=`, `>=` y `=`)
- [x] Detección de problemas no acotados e infactibles
- [x] Pruebas automáticas del método Gran M.
- [X] Implementación del método **Simplex**
- [X] Mejoras visuales de la interfaz
- [x] Pruebas automáticas del método Simplex.

## Estructura

| Archivo         | Capa        | Qué hace                                      |
| --------------- | ----------- | --------------------------------------------- |
| `Model.py`      | Modelo      | Lógica matemática (algoritmo y tablas)        |
| `View.py`       | Vista       | Ventana y widgets de Tkinter                  |
| `Controller.py` | Controlador | Conecta vista y modelo; punto de entrada      |
| `test.py`       | Pruebas     | Casos de prueba con `pytest`                  |

## Requisitos

- Python 3.10 o superior (Tkinter viene incluido en la instalación estándar)
- `numpy`

```bash
pip install numpy
```

## Uso

```bash
python Controller.py
```

1. Escribe el número de variables y pulsa **Configurar**.
2. Elige Maximizar/Minimizar e ingresa los coeficientes de Z.
3. Añade las restricciones con **+ Añadir Restricción**.
4. Pulsa **Resolver modelo** (o `Enter` en el último campo).

Con `Enter` se avanza de campo en campo; un campo vacío se toma como `0`.

## Pruebas

```bash
pip install pytest
pytest test.py -v
```
