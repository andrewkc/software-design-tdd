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


def _dias_hasta_vencimiento(lote: dict, fecha_actual: date) -> int:
    return (lote["vence"] - fecha_actual).days


def estado_lote(lote: dict, fecha_actual: date) -> tuple[str, str]:
    # Los bloqueos del personal tienen prioridad sobre la fecha.
    if lote["deteriorado"] or lote["bloqueado"]:
        return "BLOQUEADO", "En observación: revisar y retirar de la venta"

    if lote["vence"] is None:
        if lote["perecible"]:
            return "SIN_FECHA", "Fecha sin verificar: revisar lote"

        return "NORMAL", "Fecha no aplicable"

    dias = _dias_hasta_vencimiento(lote, fecha_actual)

    if dias < 0:
        return "VENCIDO", "Vencido: retirar de la venta"

    if dias == 0:
        return "HOY", "Vence hoy: revisar antes de vender"

    if dias <= DIAS_VENTANA_ALERTA:
        return "PROXIMO", f"Vence en {dias} días: revisar lote"

    return "NORMAL", f"Vence el {lote['vence'].strftime(FORMATO_FECHA)}"
