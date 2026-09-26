from __future__ import annotations

from datetime import date

DIAS_VENTANA_ALERTA = 3

FORMATO_FECHA = "%d/%m/%Y"

BLOQUEADO = "BLOQUEADO"
SIN_FECHA = "SIN_FECHA"
VENCIDO = "VENCIDO"
HOY = "HOY"
PROXIMO = "PROXIMO"
NORMAL = "NORMAL"

ESTADOS_QUE_BLOQUEAN = frozenset({BLOQUEADO, SIN_FECHA, VENCIDO})
ESTADO_QUE_EXIGE_REVISION = HOY

TEXTO_BLOQUEADO = "En observación: revisar y retirar de la venta"
TEXTO_SIN_FECHA = "Fecha sin verificar: revisar lote"
TEXTO_VENCIDO = "Vencido: retirar de la venta"
TEXTO_HOY = "Vence hoy: revisar antes de vender"
TEXTO_PROXIMO = "Vence en {dias} días: revisar lote"
TEXTO_NORMAL = "Vence el {fecha}"
TEXTO_FECHA_NO_APLICABLE = "Fecha no aplicable"

ERROR_CANTIDAD = "La cantidad debe ser mayor que cero"
ERROR_STOCK = "No hay stock suficiente: el lote tiene {stock} y se piden {cantidad}"
ERROR_ESTADO = "No se puede vender este lote. {texto}"
ERROR_REVISION_HOY = (
    "El lote vence hoy: se requiere la revisión del personal antes de vender"
)


def _dias_hasta_vencimiento(lote: dict, fecha_actual: date) -> int:
    return (lote["vence"] - fecha_actual).days


def estado_lote(lote: dict, fecha_actual: date) -> tuple[str, str]:
    if lote["deteriorado"] or lote["bloqueado"]:
        return BLOQUEADO, TEXTO_BLOQUEADO

    if lote["vence"] is None:
        if lote["perecible"]:
            return SIN_FECHA, TEXTO_SIN_FECHA

        return NORMAL, TEXTO_FECHA_NO_APLICABLE

    dias = _dias_hasta_vencimiento(lote, fecha_actual)

    if dias < 0:
        return VENCIDO, TEXTO_VENCIDO

    if dias == 0:
        return HOY, TEXTO_HOY

    if dias <= DIAS_VENTANA_ALERTA:
        return PROXIMO, TEXTO_PROXIMO.format(dias=dias)

    return NORMAL, TEXTO_NORMAL.format(
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

    estado, texto = estado_lote(lote, fecha_venta)

    if estado in ESTADOS_QUE_BLOQUEAN:
        raise ValueError(ERROR_ESTADO.format(texto=texto))

    if estado == ESTADO_QUE_EXIGE_REVISION and not revision_hoy:
        raise ValueError(ERROR_REVISION_HOY)
