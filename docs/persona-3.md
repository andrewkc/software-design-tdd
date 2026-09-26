# Evidencias TDD

Este archivo reúne evidencias reales de las ramas integradas y del ciclo 4 ejecutado en `persona-2`.

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

## Persona 1 - validación

El módulo `src/validacion.py` y sus 23 pruebas se integraron desde `persona-1`. El detalle de los cuatro ciclos de validación y sus commits está en [persona-1.md](persona-1-validacion.md); las salidas por paso se conservan en `tests/evidencias/`.

## Persona 2 - Ciclo 4: integración

El ciclo integró `validar_venta`, `precio_aplicado` y `crear_movimiento`, en ese orden. Se añadieron cuatro pruebas para la venta promocional válida, el rechazo por deterioro, el precio regular sin promoción y la revisión del día de vencimiento.

### RED

La prueba se ejecutó antes de crear `src/venta.py`; falló al importar el módulo ausente. Extracto real: [ciclo-4-red.txt](evidencias/ciclo-4-red.txt). Commit: `50dbcd3`.

### GREEN

Se agregó la implementación mínima de `registrar_venta`. Las cuatro pruebas pasaron. Extracto real: [ciclo-4-green.txt](evidencias/ciclo-4-green.txt). Commit: `ca07f82`.

### REFACTOR

Se hicieron explícitos con argumentos nombrados los datos enviados a cada módulo. Las cuatro pruebas siguieron pasando. Extracto real: [ciclo-4-refactor.txt](evidencias/ciclo-4-refactor.txt). Commit: `5329724`.

## Suite integrada

Las suites integradas contienen 34 pruebas: 23 de validación, 5 de precios, 2 de movimientos y 4 de integración. Resultado en `persona-2` con `python -m pytest -p no:cacheprovider -q`: `34 passed in 0.07s`.
