# Evidencias TDD

Este archivo reune evidencias reales del avance. No se registran como hechos las pruebas de otros integrantes hasta que el equipo las aporte o se ejecuten en la rama integrada.

## Persona 3 - Ciclo 3: movimientos

Archivos trabajados:

- `src/movimientos.py`
- `tests/test_movimientos.py`

Responsabilidad implementada:

- Crear un movimiento de salida por venta a partir de una venta ya validada.
- Devolver un nuevo lote con stock reducido sin modificar el lote original.
- Guardar cantidad, precio aplicado, total y responsable.

### RED

Primero se escribieron las pruebas en `tests/test_movimientos.py` antes de crear `src/movimientos.py`.

Comando:

```bash
python -m pytest tests/test_movimientos.py
```

Resultado real:

```text
collected 0 items / 1 error
ModuleNotFoundError: No module named 'src.movimientos'
```

Nota: antes de este RED se detecto que pytest no estaba instalado en el entorno local (`No module named pytest`), por lo que se instalo pytest y se repitio el comando para obtener el fallo propio del ciclo TDD.

### GREEN

Se implemento el minimo codigo necesario para `crear_movimiento`.

Comando:

```bash
python -m pytest tests/test_movimientos.py
```

Resultado real:

```text
collected 2 items
tests/test_movimientos.py .. [100%]
2 passed in 0.01s
```

### REFACTOR

Se refactorizo el modulo para separar el calculo del total y dejar el motivo de venta como constante, sin cambiar la interfaz publica.

Comando:

```bash
python -m pytest tests/test_movimientos.py
```

Resultado real:

```text
collected 2 items
tests/test_movimientos.py .. [100%]
2 passed in 0.01s
```

## Pruebas de persona 3

| Prueba | Objetivo | Estado |
| --- | --- | --- |
| `test_venta_descuenta_la_cantidad_exactamente_una_vez` | Verifica que el stock baja de 5 a 3 al vender 2 unidades y que el lote original no cambia. | Pasa |
| `test_movimiento_guarda_cantidad_precio_total_y_responsable` | Verifica motivo, lote, cantidad, responsable, precio unitario y total de la venta. | Pasa |

## Aportes pendientes del equipo

| Integrante | Evidencia pendiente |
| --- | --- |
| Persona 1 | Ciclo de validacion, pruebas de cantidad, stock, vencimiento y deterioro. |
| Persona 2 | Ciclo de precios, ciclo de integracion y ejecucion final tras fusionar ramas. |
