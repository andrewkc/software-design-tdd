# Evidencias de la aplicación de TDD

## Funcionalidad y diseño

Aplicamos TDD a la confirmación de una venta de un producto desde un lote (parte de CU-05). Dividimos la lógica en validación, precio, movimiento e integración. Las pruebas fijaron el orden de las operaciones y los resultados esperados antes de cerrar cada módulo. El [contrato técnico](contrato.md) describe las interfaces y reglas compartidas.

## Ciclos y trazabilidad

| Ciclo | Comportamiento probado | RED | GREEN | REFACTOR | Evidencia |
| --- | --- | --- | --- | --- | --- |
| Validación | Estados del lote, cantidad, stock y bloqueos | Pruebas que fallan antes de implementar cada grupo de reglas | Implementación de `estado_lote` y `validar_venta` | Constantes, mensajes y separación de responsabilidades | [Detalle](persona-1.md) y salidas `tests/evidencias/ciclo-1-*` a `ciclo-4-*` |
| Precio | Precio regular o promocional aprobado, activo y vigente | `e56ed16` | `a36db56` | `5dd6daf` | [Detalle](persona-2.md) y `tests/test_precios.py` |
| Movimiento | Descuento único del stock y registro de cantidad, precio, total y responsable | Pruebas y salida de importación fallida documentadas | Dos pruebas aprobadas con el código mínimo | Cálculo del total y motivo de venta separados | [Detalle](persona-3.md) y `tests/test_movimientos.py` |
| Integración | Venta válida con promoción y rechazo sin cambiar el stock; precio regular y revisión del día | `50dbcd3` | `ca07f82` | `5329724` | [Detalle](persona-2.md) y salidas `docs/evidencias/ciclo-4-*` |

En validación conservamos cuatro secuencias de pruebas, implementación y mejora en el historial de `persona-1`. En precio e integración los commits indicados permiten comparar las etapas. En movimientos, el commit `ab5597b` incorpora el código y las dos pruebas finales; el orden de sus etapas está registrado en [persona-3.md](persona-3.md), pero no puede comprobarse solo con ese commit. Los commits `03d1a0b`, `f59c9c6` y `6e2b9b8` añadieron material documental después del código.

## Código antes y después del refactor

En el ciclo de integración, `ca07f82` pasó los argumentos por posición:

```python
validar_venta(lote, cantidad, fecha_venta, revision_hoy)
precio_unitario_centavos = precio_aplicado(
    precio_regular_centavos, promocion, fecha_venta
)
```

En `5329724` usamos nombres explícitos sin alterar el resultado:

```python
validar_venta(
    lote=lote,
    cantidad=cantidad,
    fecha_venta=fecha_venta,
    revision_hoy=revision_hoy,
)
precio_unitario_centavos = precio_aplicado(
    precio_regular_centavos=precio_regular_centavos,
    promocion=promocion,
    fecha_venta=fecha_venta,
)
```

Las cuatro pruebas de integración siguieron pasando después del cambio. Los archivos completos de ambas versiones pueden consultarse con `git show ca07f82:src/venta.py` y `git show 5329724:src/venta.py`.

## Cobertura de escenarios

| Tipo | Ejemplos comprobados |
| --- | --- |
| Normal | Venta con promoción vigente, venta con precio regular, lote vendible y movimiento completo. |
| Límite | Cantidad igual al stock, vencimiento hoy con revisión, proximidad de tres días. |
| Error | Cantidad cero o negativa, stock insuficiente, lote vencido, deteriorado, bloqueado o perecible sin fecha requerida. |

La suite contiene **34 pruebas**: 23 de validación, 5 de precio, 2 de movimiento y 4 de integración. En la rama integrada `persona-2` ejecutamos:

```text
python -m pytest -p no:cacheprovider -q
34 passed
```

La [demostración ejecutable](../demo.py) muestra una venta válida con stock de 5 a 3 y total de S/ 16,00, seguida de un rechazo por deterioro con el stock original en 5. Para repetir ambas comprobaciones:

```powershell
python demo.py
python -m pytest -p no:cacheprovider -q
```

## Impacto y límites observados

Las pruebas hicieron explícitas las reglas de cantidad, vencimiento, promoción y stock, y nos permitieron refactorizar la integración manteniendo el comportamiento comprobado. La separación de módulos evitó repetir validaciones en el cálculo del movimiento. La suite confirma estos escenarios en memoria; no mide una reducción general de defectos ni valida persistencia, permisos o ventas concurrentes. Nuestras [conclusiones](conclusiones.md) recogen el análisis del equipo.
