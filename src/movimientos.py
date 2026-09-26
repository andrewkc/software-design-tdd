MOTIVO_VENTA = "venta"


def _calcular_total(cantidad, precio_unitario_centavos):
    return cantidad * precio_unitario_centavos


def crear_movimiento(lote, cantidad, precio_unitario_centavos, responsable):
    stock_actualizado = lote["stock"] - cantidad
    nuevo_lote = {**lote, "stock": stock_actualizado}

    movimiento = {
        "motivo": MOTIVO_VENTA,
        "lote_id": lote["id"],
        "cantidad": cantidad,
        "responsable": responsable,
        "precio_unitario_centavos": precio_unitario_centavos,
        "total_centavos": _calcular_total(cantidad, precio_unitario_centavos),
    }

    return nuevo_lote, movimiento
