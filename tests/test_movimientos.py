from src.movimientos import crear_movimiento


def test_venta_descuenta_la_cantidad_exactamente_una_vez():
    lote = {"id": "L1", "stock": 5, "producto": "Leche"}

    nuevo_lote, _ = crear_movimiento(
        lote=lote,
        cantidad=2,
        precio_unitario_centavos=800,
        responsable="Persona 3",
    )

    assert nuevo_lote["stock"] == 3
    assert lote["stock"] == 5


def test_movimiento_guarda_cantidad_precio_total_y_responsable():
    lote = {"id": "L1", "stock": 5}

    _, movimiento = crear_movimiento(
        lote=lote,
        cantidad=2,
        precio_unitario_centavos=800,
        responsable="Persona 3",
    )

    assert movimiento == {
        "motivo": "venta",
        "lote_id": "L1",
        "cantidad": 2,
        "responsable": "Persona 3",
        "precio_unitario_centavos": 800,
        "total_centavos": 1600,
    }
