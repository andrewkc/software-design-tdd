# Contrato técnico de la venta desde un lote

## Funcionalidad

Implementamos una parte de CU-05: registrar la salida por venta de un producto desde un lote. La venta se ejecuta en memoria y devuelve el lote actualizado y el movimiento generado. El orden del proceso es **validar → elegir precio → crear movimiento**.

## Representación compartida

Las fechas son objetos `datetime.date`. Los importes se expresan como enteros en centavos: `1000` equivale a S/ 10,00. La promoción de entrada, cuando existe, ya fue aprobada; este flujo comprueba la marca `aprobada`, pero no implementa el proceso de aprobación.

```python
from datetime import date

lote = {
    "id": "L1",
    "stock": 5,
    "perecible": True,
    "vence": date(2026, 10, 1),
    "deteriorado": False,
    "bloqueado": False,
}

promocion = {
    "precio_centavos": 800,
    "inicio": date(2026, 9, 25),
    "fin": date(2026, 9, 30),
    "activa": True,
    "aprobada": True,
}
```

Para un producto sin fecha de vencimiento aplicable usamos `perecible=False` y `vence=None`. Un producto perecible con `vence=None` no puede venderse hasta que se registre o verifique la fecha.

## Reglas y funciones

| Función | Contrato aplicado |
| --- | --- |
| `estado_lote(lote, fecha_actual)` | Devuelve `(estado, texto)`. Prioriza deterioro o bloqueo, después falta de fecha requerida, vencimiento y proximidad. |
| `validar_venta(lote, cantidad, fecha_venta, revision_hoy=False)` | Devuelve `None` si la venta procede; lanza `ValueError` si `cantidad <= 0`, supera el stock, o el lote está bloqueado, deteriorado, vencido o carece de fecha requerida. Si vence ese día, exige `revision_hoy=True`. |
| `precio_aplicado(precio_regular_centavos, promocion, fecha_venta)` | Devuelve el precio promocional solo cuando la promoción existe, está aprobada y activa, y `inicio <= fecha_venta <= fin`; en otro caso devuelve el regular. |
| `crear_movimiento(lote, cantidad, precio_unitario_centavos, responsable)` | Recibe una venta ya validada. Devuelve `(nuevo_lote, movimiento)` sin modificar el lote original. El movimiento guarda `motivo="venta"`, `lote_id`, `cantidad`, `responsable`, `precio_unitario_centavos` y `total_centavos`. |
| `registrar_venta(lote, cantidad, fecha_venta, precio_regular_centavos, promocion, responsable, revision_hoy=False)` | Llama a validación, precio y movimiento en ese orden y devuelve `(nuevo_lote, movimiento)`. Una validación fallida detiene la operación antes de crear el movimiento. |

La fecha de vencimiento es el último día permitido en esta demostración, siempre que el personal haya realizado la revisión y se pase `revision_hoy=True`. Esa marca registra una acción humana; no certifica la inocuidad del producto. Un lote deteriorado o bloqueado se rechaza incluso con esa marca. La ventana informativa de proximidad es de tres días y no modifica estas reglas de venta.

## Resultado de referencia

Con stock inicial de 5, cantidad 2 y promoción vigente de 800 centavos por unidad, el resultado es stock **3** y total **1600 centavos (S/ 16,00)**. El lote de entrada conserva stock 5.

## Límites

El contrato supone que los datos de la promoción aprobada son válidos: precio positivo, inferior al regular y fechas ordenadas. No implementamos persistencia, varias líneas de venta, permisos, revalidación frente a concurrencia, cancelaciones, mermas ni sugerencias de IA.
