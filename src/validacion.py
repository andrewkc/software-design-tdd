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


def estado_lote(lote: dict, fecha_actual: date) -> tuple[str, str]:
    dias = (lote["vence"] - fecha_actual).days

    if dias < 0:
        return "VENCIDO", "Vencido: retirar de la venta"

    if dias == 0:
        return "HOY", "Vence hoy: revisar antes de vender"

    if dias <= 3:
        return "PROXIMO", f"Vence en {dias} días: revisar lote"

    return "NORMAL", f"Vence el {lote['vence'].strftime('%d/%m/%Y')}"
