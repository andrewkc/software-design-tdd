from datetime import date

import pytest

from src.venta import registrar_venta


FECHA_VENTA = date(2026, 9, 27)
PROMOCION_VIGENTE = {
    "precio_centavos": 800,
    "inicio": date(2026, 9, 25),
    "fin": date(2026, 9, 30),
    "activa": True,
    "aprobada": True,
}


def lote_vendible(**cambios):
    lote = {
        "id": "L1",
        "stock": 5,
        "perecible": True,
        "vence": date(2026, 10, 1),
        "deteriorado": False,
        "bloqueado": False,
    }
    lote.update(cambios)
    return lote


def test_venta_valida_aplica_promocion_y_registra_movimiento():
    lote = lote_vendible()

    nuevo_lote, movimiento = registrar_venta(
        lote,
        2,
        FECHA_VENTA,
        1000,
        PROMOCION_VIGENTE,
        "Ana",
    )

    assert nuevo_lote["stock"] == 3
    assert lote["stock"] == 5
    assert movimiento == {
        "motivo": "venta",
        "lote_id": "L1",
        "cantidad": 2,
        "responsable": "Ana",
        "precio_unitario_centavos": 800,
        "total_centavos": 1600,
    }


def test_venta_rechazada_por_deterioro_no_cambia_stock():
    lote = lote_vendible(deteriorado=True)

    with pytest.raises(ValueError, match="observación"):
        registrar_venta(lote, 2, FECHA_VENTA, 1000, PROMOCION_VIGENTE, "Ana")

    assert lote["stock"] == 5


def test_venta_sin_promocion_usa_precio_regular():
    _, movimiento = registrar_venta(
        lote_vendible(), 2, FECHA_VENTA, 1000, None, "Ana"
    )

    assert movimiento["precio_unitario_centavos"] == 1000
    assert movimiento["total_centavos"] == 2000


def test_venta_que_vence_hoy_reenvia_revision_del_personal():
    lote = lote_vendible(vence=FECHA_VENTA)

    nuevo_lote, _ = registrar_venta(
        lote,
        1,
        FECHA_VENTA,
        1000,
        None,
        "Ana",
        revision_hoy=True,
    )

    assert nuevo_lote["stock"] == 4