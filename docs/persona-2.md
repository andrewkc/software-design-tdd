# TDD de ventas desde un lote

Este documento reúne el contrato técnico, los módulos integrados y los ciclos de persona 2 para la demostración parcial de CU-05.

## Módulos integrados

- `src/validacion.py`: calcula el estado del lote y rechaza ventas inválidas. Un lote que vence hoy requiere `revision_hoy=True`.
- `src/precios.py`: aplica el precio promocional únicamente si la promoción está aprobada, activa y vigente.
- `src/movimientos.py`: devuelve una copia del lote con el stock reducido y el movimiento con responsable, precio y total.
- `src/venta.py`: coordina primero la validación, después la selección de precio y por último la creación del movimiento.

Los importes son enteros en centavos y las fechas son `datetime.date`. La demostración funciona en memoria y no implementa persistencia ni todas las reglas de CU-05.

## Ciclo 2: precio promocional

`tests/test_precios.py` cubre el precio regular sin promoción, la promoción vigente, la promoción vencida, la falta de aprobación y la promoción inactiva. Los resultados RED, GREEN y REFACTOR se registraron con Python 3.13.5 y pytest 8.3.4. Los cinco casos pasan.

El refactor extrajo `_promocion_vigente` para separar la regla de vigencia de la selección del importe. La interfaz pública se mantuvo sin cambios.

## Ciclo 4: integración de la venta

`registrar_venta(lote, cantidad, fecha_venta, precio_regular_centavos, promocion, responsable, revision_hoy=False)` devuelve `(nuevo_lote, movimiento)`. Las cuatro pruebas de `tests/test_venta.py` comprueban:

- Venta válida con promoción: stock de 5 a 3, precio unitario de 800 y total de 1600 centavos.
- Rechazo de lote deteriorado sin cambiar el stock original.
- Uso del precio regular cuando no hay promoción.
- Reenvío de `revision_hoy=True` para una venta en la fecha de vencimiento.

| Etapa | Commit | Resultado real |
| --- | --- | --- |
| RED | `50dbcd3` | Falló la importación: `src.venta` aún no existía. |
| GREEN | `ca07f82` | 4 pruebas pasaron. |
| REFACTOR | `5329724` | 4 pruebas pasaron tras hacer explícitos los argumentos entre módulos. |

Los extractos de salida están en [evidencias.md](evidencias.md) y en `docs/evidencias/ciclo-4-*.txt`.

## Ejecutar la suite integrada

```powershell
python -m pytest -p no:cacheprovider -q
```

La documentación de validación está en [persona-1-validacion.md](persona-1-validacion.md). Las evidencias de los ciclos 1 a 3 se conservan en [evidencias.md](evidencias.md).

