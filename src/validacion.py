"""Validacion de la venta de un lote (CU-05).

Modulo a cargo de la persona 1 del Grupo 2. Implementa las dos
funciones que fija el acuerdo tecnico:

- estado_lote:   etiqueta interna de vencimiento y su texto.
- validar_venta: bloquea la venta cuando alguna regla no se cumple.

Las etiquetas son informacion operativa para el personal, no una
certificacion sanitaria: el sistema no decide si un producto es apto.
"""

from __future__ import annotations

from datetime import date

# Decision del equipo para este prototipo (seccion 3 del acuerdo).
# No representa una garantia sanitaria: si el equipo la cambia, se
# actualiza aqui y en el acuerdo.
DIAS_VENTANA_ALERTA = 3

FORMATO_FECHA = "%d/%m/%Y"

# Textos de la tabla de la seccion 3 del acuerdo. Estan juntos para
# que una correccion de redaccion se haga en un solo lugar y no se
# desincronice con lo que acordo el equipo.
TEXTO_BLOQUEADO = "En observación: revisar y retirar de la venta"
TEXTO_SIN_FECHA = "Fecha sin verificar: revisar lote"
TEXTO_VENCIDO = "Vencido: retirar de la venta"
TEXTO_HOY = "Vence hoy: revisar antes de vender"
TEXTO_PROXIMO = "Vence en {dias} días: revisar lote"
TEXTO_NORMAL = "Vence el {fecha}"
TEXTO_FECHA_NO_APLICABLE = "Fecha no aplicable"

# Mensajes de los errores que bloquean la venta.
ERROR_CANTIDAD = "La cantidad debe ser mayor que cero"
ERROR_STOCK = "No hay stock suficiente: el lote tiene {stock} y se piden {cantidad}"


def _dias_hasta_vencimiento(lote: dict, fecha_actual: date) -> int:
    return (lote["vence"] - fecha_actual).days


def estado_lote(lote: dict, fecha_actual: date) -> tuple[str, str]:
    """Etiqueta interna del lote y el texto que ve el personal.

    El orden de evaluacion es el de la tabla del acuerdo: los bloqueos
    del personal pesan mas que cualquier estado de fecha.
    """
    if lote["deteriorado"] or lote["bloqueado"]:
        return "BLOQUEADO", TEXTO_BLOQUEADO

    if lote["vence"] is None:
        if lote["perecible"]:
            return "SIN_FECHA", TEXTO_SIN_FECHA

        return "NORMAL", TEXTO_FECHA_NO_APLICABLE

    dias = _dias_hasta_vencimiento(lote, fecha_actual)

    if dias < 0:
        return "VENCIDO", TEXTO_VENCIDO

    if dias == 0:
        return "HOY", TEXTO_HOY

    if dias <= DIAS_VENTANA_ALERTA:
        return "PROXIMO", TEXTO_PROXIMO.format(dias=dias)

    return "NORMAL", TEXTO_NORMAL.format(
        fecha=lote["vence"].strftime(FORMATO_FECHA)
    )


def validar_venta(
    lote: dict,
    cantidad: int,
    fecha_venta: date,
    revision_hoy: bool = False,
) -> None:
    if cantidad <= 0:
        raise ValueError(ERROR_CANTIDAD)

    if cantidad > lote["stock"]:
        raise ValueError(
            ERROR_STOCK.format(stock=lote["stock"], cantidad=cantidad)
        )
