# TDD aplicado a ventas de bodegas

Repositorio del trabajo de Diseño de Software para demostrar TDD sobre una parte acotada de CU-05: confirmar una venta de un producto desde un lote.

## Alcance de esta rama

Rama: `persona-3`

La parte de persona 3 implementa el ciclo 3:

- Modulo: `src/movimientos.py`
- Pruebas: `tests/test_movimientos.py`
- Funcion: `crear_movimiento(lote, cantidad, precio_unitario_centavos, responsable)`

Esta funcion recibe una venta ya validada por los modulos de validacion e integracion. Su responsabilidad es devolver un nuevo lote con el stock reducido y un registro de salida por venta con lote, cantidad, responsable, precio aplicado y total.

## Contrato usado

La funcion de persona 3 sigue el contrato compartido:

```python
crear_movimiento(lote, cantidad, precio_unitario_centavos, responsable) -> tuple[dict, dict]
```

Reglas cubiertas por esta parte:

- No modifica el diccionario original del lote.
- Descuenta el stock exactamente una vez: `stock - cantidad`.
- Crea un movimiento con `motivo = "venta"`.
- Guarda `lote_id`, `cantidad`, `responsable`, `precio_unitario_centavos` y `total_centavos`.
- Calcula el total como `cantidad * precio_unitario_centavos`.

## Ejecucion de pruebas

Instalar pytest si el entorno aun no lo tiene:

```bash
python -m pip install pytest
```

Ejecutar las pruebas de persona 3:

```bash
python -m pytest tests/test_movimientos.py
```

Resultado verificado en esta rama:

```text
2 passed
```

## Pendiente de integracion

Las validaciones de cantidad, stock suficiente, vencimiento y deterioro corresponden a persona 1. El precio aplicado y la funcion integradora de venta corresponden a persona 2. Esta rama no implementa esas partes para mantener el alcance acordado.
