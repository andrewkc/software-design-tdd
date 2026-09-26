# software-design-tdd

Registro de una venta desde un lote (CU-05), desarrollado con
**Test-Driven Development**.

Trabajo grupal del curso Diseño de Software — **Grupo 2**.

## Integrantes

- Diaz Ysla, Walter Alexander
- Champi Hinojosa, Miguel Angel
- Cahuana Condori, Kelvin Andreí

## De qué trata

Una bodega vende productos que vencen. Antes de cobrar hay que
responder tres preguntas: **¿se puede vender este lote?**, **¿a qué
precio?** y **¿cómo queda el stock?**

El sistema las resuelve en ese orden. Si la primera falla, no hay venta
ni movimiento ni cambio de stock.

```
registrar_venta
      │
      ├─ 1. validar_venta      ¿se puede vender?    → ValueError si no
      ├─ 2. precio_aplicado    ¿a qué precio?
      └─ 3. crear_movimiento   ¿cómo queda el stock?
```

Es una demostración de la metodología, en memoria: no hay base de
datos, ni varias líneas por venta, ni permisos, ni concurrencia.

## Cómo funciona la validación

Esta rama contiene el **módulo de validación** (`src/validacion.py`),
que es el primer paso de la cadena.

### Los datos

Un lote es un diccionario. Las fechas son `datetime.date` y el dinero
son **enteros en centavos** (`1000` = S/ 10,00), para evitar los
errores de redondeo del punto flotante.

```python
lote = {
    "id": "L1",
    "stock": 5,
    "perecible": True,
    "vence": date(2026, 10, 1),
    "deteriorado": False,
    "bloqueado": False,   # envase dañado o conservación dudosa
}
```

`deteriorado` y `bloqueado` son marcas que registra el personal. El
sistema no decide por su cuenta si un producto está en buen estado.

### `estado_lote(lote, fecha_actual)`

Devuelve una etiqueta y el texto que ve el personal. Evalúa en este
orden, y el orden importa: **los bloqueos del personal pesan más que
cualquier fecha.**

| Condición | Estado | Texto | Venta |
|---|---|---|---|
| `deteriorado` o `bloqueado` | `BLOQUEADO` | «En observación: revisar y retirar de la venta» | Bloqueada |
| Perecible sin fecha registrada | `SIN_FECHA` | «Fecha sin verificar: revisar lote» | Bloqueada |
| Ya venció | `VENCIDO` | «Vencido: retirar de la venta» | Bloqueada |
| Vence hoy | `HOY` | «Vence hoy: revisar antes de vender» | Solo tras revisión |
| Vence en 1 a 3 días | `PROXIMO` | «Vence en X días: revisar lote» | Permitida |
| Falta más tiempo, o no aplica fecha | `NORMAL` | «Vence el DD/MM/AAAA» o «Fecha no aplicable» | Permitida |

La ventana de alerta de 3 días es una decisión del equipo para este
prototipo. No representa una garantía sanitaria.

```python
>>> estado_lote({...  "vence": date(2026, 10, 4)}, date(2026, 10, 1))
('PROXIMO', 'Vence en 3 días: revisar lote')
```

### `validar_venta(lote, cantidad, fecha_venta, revision_hoy=False)`

No devuelve nada: deja pasar la venta o la corta con `ValueError`.
Rechaza cuando

- la cantidad no es positiva,
- la cantidad supera el stock,
- el estado del lote es `BLOQUEADO`, `SIN_FECHA` o `VENCIDO`,
- el lote vence hoy y no se registró la revisión del personal.

```python
>>> validar_venta(lote_normal, 2, hoy)          # pasa, devuelve None
>>> validar_venta(lote_vencido, 2, hoy)
ValueError: No se puede vender este lote. Vencido: retirar de la venta
```

**El día del vencimiento** la venta procede solo si el empleado revisó
rotulado, envase y conservación, e informó al comprador. Eso se
registra con `revision_hoy=True`: es el registro de una acción humana,
no una certificación automática.

Un detalle que conviene tener claro: **esa revisión no habilita un lote
deteriorado**. Como el bloqueo se evalúa antes que la fecha, un lote
marcado como deteriorado se rechaza aunque se pase `revision_hoy=True`.

## Cómo correr las pruebas

Desde la raíz del repositorio:

```bash
python -m pip install pytest
python -m pytest tests/test_validacion.py
```

```
23 passed
```

## Estructura

```
src/validacion.py              Estado del lote y validación de la venta
tests/test_validacion.py       Las 23 pruebas, numeradas por ciclo
tests/evidencias/              Salida real de pytest en cada RED y GREEN
docs/persona-1-validacion.md   Sustento del módulo y de los ciclos TDD
```

## Metodología

El módulo se construyó en cuatro ciclos **RED → GREEN → REFACTOR**, y
cada ciclo dejó sus commits en el historial. La prueba siempre entró
antes que el código que la satisface.

```bash
git log --oneline --reverse
```

El detalle de cada ciclo está en
[docs/persona-1-validacion.md](docs/persona-1-validacion.md).
